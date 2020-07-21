import tensorflow as tf
from nmt.transformer import *


MAX_SEQ_LENGTH = 128


def encode_ind(ind, tokenizer_ind):
    tokens_ind = tokenizer_ind.tokenize(ind)
    lang1 = tokenizer_ind.convert_tokens_to_ids(['[CLS]'] + tokens_ind + ['[SEP]'])

    return lang1

def evaluate(transformer, inp_sentence, tokenizer_en, tokenizer_ind):
    # normalize input sentence
    inp_sentence = encode_ind(inp_sentence, tokenizer_ind)
    encoder_input = tf.expand_dims(inp_sentence, 0)

    # as the target is english, the first word to the transformer should be the
    # english start token.
    decoder_input = [tokenizer_en.vocab_size]
    output = tf.expand_dims(decoder_input, 0)

    for i in range(MAX_SEQ_LENGTH):
        combined_mask, dec_padding_mask = create_masks(
            encoder_input, output)

        # predictions.shape == (batch_size, seq_len, vocab_size)
        predictions, attention_weights = transformer(encoder_input,
                                                     output,
                                                     False,
                                                     combined_mask,
                                                     dec_padding_mask)

        # select the last word from the seq_len dimension
        predictions = predictions[:, -1:, :]  # (batch_size, 1, vocab_size)

        predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)

        # return the result if the predicted_id is equal to the end token
        if tf.equal(predicted_id, tokenizer_en.vocab_size + 1):
            return tf.squeeze(output, axis=0), attention_weights

        # concatentate the predicted_id to the output which is given to the decoder
        # as its input.
        output = tf.concat([output, predicted_id], axis=-1)

    return tf.squeeze(output, axis=0), attention_weights

def translate(transformer, sentence, tokenizer_en, tokenizer_ind):
    result, attention_weights = evaluate(transformer, sentence, tokenizer_en, tokenizer_ind)

    predicted_sentence = tokenizer_en.decode([i for i in result
                                              if i < tokenizer_en.vocab_size])

    print('Input: {}'.format(sentence))
    print('Predicted translation: {}'.format(predicted_sentence))

    return predicted_sentence