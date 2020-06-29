
import os
import sys
import threading

sys.path.append('./../')
from flask import Flask, render_template, request
from flask_wtf import FlaskForm


import utils.translate_utils as tx

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    The flask server renders a HTML page which can read
    in two queries, which are then used by this function
    to generate the rewritten queries, which will then
    be shown on the page.

    Prediction is offloaded to the GPU using two separate 
    threads.
    """
    form = FlaskForm()

    if form.is_submitted():
        query1 = request.form['query1']
        query2 = request.form['query2']

        processed_query1 = tx.translate_text(query1)
        processed_query2 = tx.translate_text(query2)

        file1 = open('inp_server.txt', 'wb')
        file1.write(" . \t {0} <::::> {1} \n".format(
            processed_query1.strip(), processed_query2.strip()).encode())
        file1.close()

        file2 = open('inp_server_hi.txt', 'wb')
        file2.write(" . \t {0} <::::> {1} \n".format(query1.strip(),
                                                     query2).encode())
        file2.close()

        thread1 = threading.Thread(
            target=os.system,
            args=
            ("bash ./../contextual-query-rewrites.sh enLT predict wikifuse 0 \
                    in_server.txt op_server.txt",
             ))
        thread2 = threading.Thread(
            target=os.system,
            args=
            ("bash ./../contextual-query-rewrites.sh hiLT predict wikifuse 0 \
                    in_server.txt op_server.txt",
             ))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        file1_op = open("op_server.txt", 'r')
        file2_op = open("op_server_hi.txt", 'r')

        processed_op_en = file1_op.readlines()[0].split('\t')[1]
        processed_op_hi = file2_op.readlines()[0].split('\t')[1]

        file1_op.close()
        file2_op.close()

        translated_text = tx.translate_text_hi(processed_op_en)
        return render_template('contextual_query_rewrites.html',
                               label1="en-LT:{0}".format(translated_text),
                               label2="hi-LT:{0}".format(processed_op_hi))

    return render_template('contextual_query_rewrites.html', label=None)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
