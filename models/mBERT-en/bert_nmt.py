from __future__ import absolute_import, division, print_function, unicode_literals

from nmt.bert_tokenization import *
from nmt.transformer import *
from nmt.translate import *

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds

import time
import numpy as np
import matplotlib.pyplot as plt
import collections
import unicodedata

import os
import sys
from bert import BertModelLayer
from bert.loader import StockBertConfig, load_stock_weights
from bert.loader import map_to_stock_variable_name

MAX_SEQ_LENGTH = 128
BUFFER_SIZE = 50000
BATCH_SIZE = 32

tokenizer_ind = FullTokenizer(
    vocab_file='multi_cased_L-12_H-768_A-12/vocab.txt', do_lower_case=True)


def get_sentences(filename):
    data = open(filename).readlines()

    sents = []

    i = 0
    for line in data:
        i += 1

        splits = line.split('\t')
        sents.append([splits[3], splits[4]])

    return sents


@tf.function
def train_step(transformer, inp, tar, optimizer, loss_function, train_loss,
               train_accuracy):
    tar_inp = tar[:, :-1]
    tar_real = tar[:, 1:]

    combined_mask, dec_padding_mask = create_masks(inp, tar_inp)

    with tf.GradientTape() as tape:
        predictions, _ = transformer(inp, tar_inp, True, combined_mask,
                                     dec_padding_mask)
        loss = loss_function(tar_real, predictions)

    gradients = tape.gradient(loss, transformer.trainable_variables)
    optimizer.apply_gradients(zip(gradients, transformer.trainable_variables))

    train_loss(loss)
    train_accuracy(tar_real, predictions)


def encode(ind, en, seq_length=MAX_SEQ_LENGTH):
    tokens_ind = tokenizer_ind.tokenize(tf.compat.as_text(ind.numpy()))
    lang1 = tokenizer_ind.convert_tokens_to_ids(['[CLS]'] + tokens_ind +
                                                ['[SEP]'])
    if len(lang1) < seq_length:
        lang1 = lang1 + list(np.zeros(seq_length - len(lang1), 'int32'))

    lang2 = [tokenizer_en.vocab_size] + tokenizer_en.encode(
        tf.compat.as_text(en.numpy())) + [tokenizer_en.vocab_size + 1]
    if len(lang2) < seq_length:
        lang2 = lang2 + list(np.zeros(seq_length - len(lang2), 'int32'))

    return lang1, lang2


def filter_max_length(x, y, max_length=MAX_SEQ_LENGTH):
    return tf.logical_and(tf.size(x) <= max_length, tf.size(y) <= max_length)


def train(dataset_file, bert_dir, checkpoint_dir):

    sentences = get_sentences(dataset_file)

    datasets = tf.data.Dataset.from_tensor_slices(sentences)

    train_examples = datasets.take(273885 // 10 * 9)
    validation_examples = datasets.skip(273885 // 10 * 9)

    global tokenizer_en
    vocab_file = 'vocab_en_'
    if os.path.isfile(vocab_file + '.subwords'):
        tokenizer_en = tfds.features.text.SubwordTextEncoder.load_from_file(
            vocab_file)
    else:
        tokenizer_en = tfds.features.text.SubwordTextEncoder.build_from_corpus(
            (en.numpy() for en, ind in train_examples),
            target_vocab_size=2**13)
    tokenizer_en.save_to_file('vocab_en_')

    train_dataset = train_examples.map(lambda sent: tf.py_function(
        encode, [sent[1], sent[0]], [tf.int32, tf.int32]))
    train_dataset = train_dataset.filter(filter_max_length)

    train_dataset = train_dataset.cache()
    train_dataset = train_dataset.shuffle(BUFFER_SIZE).padded_batch(
        BATCH_SIZE, padded_shapes=([-1], [-1]), drop_remainder=True)
    train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)

    val_dataset = validation_examples.map(lambda sent: tf.py_function(
        encode, [sent[1], sent[0]], [tf.int32, tf.int32]))
    val_dataset = val_dataset.filter(filter_max_length)
    val_dataset = val_dataset.padded_batch(BATCH_SIZE,
                                           padded_shapes=([-1], [-1]))

    temp_mha = MultiHeadAttention(d_model=512, num_heads=8)
    y = tf.random.uniform((1, 60, 768))
    q = tf.random.uniform((1, 60, 512))
    out, attn = temp_mha(y, k=y, q=q, mask=None)

    sample_decoder_layer = DecoderLayer(512, 8, 2048)
    sample_encoder_output = tf.random.uniform((64, 128, 768))

    sample_decoder_layer_output, _, _ = sample_decoder_layer(
        tf.random.uniform((64, 50, 512)), sample_encoder_output, False, None,
        None)

    sample_decoder = Decoder(num_layers=2,
                             d_model=512,
                             num_heads=8,
                             dff=2048,
                             target_vocab_size=8000)

    output, attn = sample_decoder(tf.random.uniform((64, 26)),
                                  enc_output=sample_encoder_output,
                                  training=False,
                                  look_ahead_mask=None,
                                  padding_mask=None)

    target_vocab_size = tokenizer_en.vocab_size + 2
    config = Config(num_layers=6, d_model=256, dff=1024, num_heads=8)

    bert_config_file = os.path.join(bert_dir, "bert_config.json")
    bert_ckpt_file = os.path.join(bert_dir, "bert_model.ckpt")

    transformer = Transformer(config=config,
                              target_vocab_size=target_vocab_size,
                              bert_config_file=bert_config_file)

    inp = tf.random.uniform((BATCH_SIZE, MAX_SEQ_LENGTH))
    tar_inp = tf.random.uniform((BATCH_SIZE, MAX_SEQ_LENGTH))
    fn_out, _ = transformer(inp,
                            tar_inp,
                            True,
                            look_ahead_mask=None,
                            dec_padding_mask=None)

    # init bert pre-trained weights
    transformer.restore_encoder(bert_ckpt_file)

    transformer.summary()

    learning_rate = CustomSchedule(config.d_model)

    optimizer = tf.keras.optimizers.Adam(learning_rate,
                                         beta_1=0.9,
                                         beta_2=0.98,
                                         epsilon=1e-9)

    temp_learning_rate_schedule = CustomSchedule(config.d_model)

    train_loss = tf.keras.metrics.Mean(name='train_loss')
    train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(
        name='train_accuracy')

    ckpt = tf.train.Checkpoint(transformer=transformer, optimizer=optimizer)

    ckpt_manager = tf.train.CheckpointManager(ckpt,
                                              checkpoint_dir,
                                              max_to_keep=5)

    # if a checkpoint exists, restore the latest checkpoint.
    if ckpt_manager.latest_checkpoint:
        ckpt.restore(ckpt_manager.latest_checkpoint)
        print('Latest checkpoint restored!!')

    EPOCHS = 10

    for epoch in range(EPOCHS):
        start = time.time()

        train_loss.reset_states()
        train_accuracy.reset_states()

        # inp -> indic, tar -> english
        for (batch, (inp, tar)) in enumerate(train_dataset):
            train_step(transformer, inp, tar, optimizer, loss_function,
                       train_loss, train_accuracy)

            if batch % 50 == 0:
                print('Epoch {} Batch {} Loss {:.4f} Accuracy {:.4f}'.format(
                    epoch + 1, batch, train_loss.result(),
                    train_accuracy.result()))

        if (epoch + 1) % 1 == 0 or batch % 100 == 0:
            ckpt_save_path = ckpt_manager.save()
            print('Saving checkpoint for epoch {} at {}'.format(
                epoch + 1, ckpt_save_path))

        print('Epoch {} Loss {:.4f} Accuracy {:.4f}'.format(
            epoch + 1, train_loss.result(), train_accuracy.result()))

        print('Time taken for 1 epoch: {} secs\n'.format(time.time() - start))

    transformer.save_weights('bert_nmt_ckpt')


def test(input_file, output_file, bert_dir):
    global tokenizer_en

    vocab_file = 'vocab_en_'

    tokenizer_en = tfds.features.text.SubwordTextEncoder.load_from_file(
        vocab_file)

    config = Config(num_layers=6, d_model=256, dff=1024, num_heads=8)
    target_vocab_size = tokenizer_en.vocab_size + 2
    bert_config_file = os.path.join(bert_dir, "bert_config.json")

    new_transformer = Transformer(config=config,
                                  target_vocab_size=target_vocab_size,
                                  bert_config_file=bert_config_file)

    inp = tf.random.uniform((BATCH_SIZE, MAX_SEQ_LENGTH))
    tar_inp = tf.random.uniform((BATCH_SIZE, MAX_SEQ_LENGTH))
    
    fn_out, _ = new_transformer(inp,
                                tar_inp,
                                True,
                                look_ahead_mask=None,
                                dec_padding_mask=None)
    
    new_transformer.load_weights('bert_nmt_ckpt')

    to_translate = open(input_file).readlines()
    translations = open(output_file, 'wb')

    for line in to_translate:
        translations.write(
            translate(new_transformer, line, tokenizer_en,
                      tokenizer_ind).encode() + '\n'.encode())

    translations.close()


if __name__ == '__main__':
    if (sys.argv[1] == 'train'):
        train(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        test(sys.argv[2], sys.argv[3], sys.argv[4])
