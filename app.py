from flask import request
from flask import Flask
from flask import render_template
from flask import make_response
from flask import request

app = Flask(__name__)

from email import policy
from email.parser import BytesParser

def render_smtp(smtpdata):
    msg = BytesParser(policy=policy.default).parsebytes(bytes(smtpdata, 'utf-8'))
    msg_body = msg.get_body(preferencelist=('html','plain'))
    content_type = msg_body['content-type']
    attachments = []
    if content_type:
        is_plain = content_type.content_type == 'text/plain'
        if content_type.content_type == 'multipart/related':
            for part in msg_body.iter_attachments():
                filename = part.get_filename()
                attachments.append(filename)
    else:
        is_plain = True

    resp = make_response(render_template('render.html',
        hdr_from=msg['from'],
        hdr_to=msg['to'],
        hdr_date=msg['date'],
        hdr_subject=msg['subject'],
        body_content=msg_body.get_content(),
        content_type='plain' if is_plain else 'html',
        attachments=attachments,
        raw_data=smtpdata))

    resp.headers['Content-Security-Policy'] = "default-src 'none'"

    return resp

@app.route('/', methods=['GET', 'POST'])
def index(name=None):
    if request.method == 'POST':
        return render_smtp(request.form['smtpdata'])
    else:
        return render_template('index.html')
