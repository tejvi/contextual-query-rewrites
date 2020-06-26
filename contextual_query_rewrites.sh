# $ bash contextual_query_rewrites.sh <en_LT|hi_LT> <preprocess|train|export|predict> <input_format>
#   <0|1> <input path for predict> <output path for predict>
# <0|1> is to specify if there is a tune set.


########## EDIT THE PATHS IN THIS SECTION##############
TUNE_DATA="path_to_tune_data"
TRAIN_DATA="path_to_train_data"
BERT_DIR="path_to_bert_dir"
MBERT_DIR="path_to_mbert_dir"
OUTPUT_DIR="path_to_output_dir"
CONFIG_FILE="path_to_config"
CONFIG_FILE_MBERT="path_to_config_mbert"
EXPNAME="exported_model_name"
LT_DIR="./models/lasertagger"
NUM_TRAIN_EXAMPLES=1000
NUM_EVAL_EXAMPLES=12
########################################################

TUNE=$4

PREPROCESS="preprocess"
TRAIN="train"
PREDICT="predict"
EXP="export"

hiLT="hi_LT"
enLT="en_LT"

BERT=$BERT_DIR
if [[ "$1" == "$hiLT" ]]; then 
    BERT=$MBERT_DIR
fi

CONFIG=$CONFIG_FILE
if [[ "$1" == "$hiLT" ]]; then
    CONFIG=$CONFIG_FILE_MBERT
fi

if [[ "$2" == "$PREPROCESS" ]]; then
    touch ${OUTPUT_DIR}/${1}_label_map.txt

    python3 ${LT_DIR}/phrase_vocabulary_optimization.py \
        --input_file=${TRAIN_DATA} \
        --input_format=${3} \
        --vocabulary_size=500 \
        --max_input_examples=1000000 \
        --output_file=${OUTPUT_DIR}/${1}_label_map.txt

    if [[ $TUNE == 1 ]]; then
        python3 ${LT_DIR}/preprocess_main.py \
            --input_file=${TUNE_DATA} \
            --input_format=$3 \
            --output_tfrecord=${OUTPUT_DIR}/${1}_tune.tf_record \
            --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
            --vocab_file=${BERT}/vocab.txt \
            --output_arbitrary_targets_for_infeasible_examples=true
    fi

    python3 ${LT_DIR}/preprocess_main.py \
        --input_file=$TRAIN_DATA \
        --input_format=$3 \
        --output_tfrecord=${OUTPUT_DIR}/${1}_train.tf_record \
        --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
        --vocab_file=$BERT/vocab.txt \
        --output_arbitrary_targets_for_infeasible_examples=false
    

elif [[ "$2" == "$TRAIN" ]]; then
    if [[ $TUNE == 1 ]]; then
        python3 ${LT_DIR}/run_lasertagger.py \
                --training_file=${OUTPUT_DIR}/${1}_train.tf_record \
                --eval_file=${OUTPUT_DIR}/${1}_tune.tf_record \
                --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
                --model_config_file=${CONFIG} \
                --output_dir=${OUTPUT_DIR}/models/$1 \
                --init_checkpoint=${BERT}/bert_model.ckpt \
                --do_train=true \
                --do_eval=true \
                --train_batch_size=256 \
                --save_checkpoints_steps=500 \
                --num_train_examples=${NUM_TRAIN_EXAMPLES} \
                --num_eval_examples=${NUM_EVAL_EXAMPLES}
    else
        python3 ${LT_DIR}/run_lasertagger.py \
                --training_file=${OUTPUT_DIR}/${1}_train.tf_record \
                --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
                --model_config_file=${CONFIG} \
                --output_dir=${OUTPUT_DIR}/models/${1} \
                --init_checkpoint=${BERT}/bert_model.ckpt \
                --do_train=true \
                --do_eval=false \
                --train_batch_size=256 \
                --save_checkpoints_steps=500 \
                --num_train_examples=${NUM_TRAIN_EXAMPLES} 
    fi
elif [[ $2 == "$EXP" ]]; then
    python3 ${LT_DIR}/run_lasertagger.py \
            --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
            --model_config_file=${CONFIG} \
            --output_dir=${OUTPUT_DIR}/models/${1} \
            --do_export=true \
            --export_path=${OUTPUT_DIR}/models/${1}/export

elif [[ "$2" == "$PREDICT" ]]; then
    
    if [[ "$1" == "$enLT" ]]; then
        python3 ./models/english_lasertagger/preprocess.py ${5}
        
        python3 ${LT_DIR}/predict_main.py \
            --input_file=${5}_translated.tsv \
            --input_format=${3} \
            --output_file=$6 \
            --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
            --vocab_file=${BERT}/vocab.txt \
            --saved_model=${OUTPUT_DIR}/models/${1}/export/${EXPNAME}

        python3 ./models/english_lasertagger/postprocess.py ${6}
    
    else
        
        python3 ${LT_DIR}/predict_main.py \
            --input_file=${5} \
            --input_format=${3} \
            --output_file=${6} \
            --label_map_file=${OUTPUT_DIR}/${1}_label_map.txt \
            --vocab_file=${BERT}/vocab.txt \
            --saved_model=${OUTPUT_DIR}/models/${1}/export/${EXPNAME}

    fi
fi



