import os
import re
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_from_directory
)
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Regexp, NumberRange
from werkzeug.security import check_password_hash, generate_password_hash
import logging

# Import internal functions
from minigotchi.config_loader import load_config
from minigotchi.pwnagotchi1 import do_scan, do_deauth, do_brute

# App setup
cfg = load_config()
app = Flask(__name__)
app.secret_key = os.getenv('MINIGOTCHI_SECRET') or os.urandom(24)
csrf = CSRFProtect(app)

# Simple login config
USER = cfg.get('web_user', 'admin')
PW_HASH = cfg.get('web_password_hash') or generate_password_hash(cfg.get('web_password', 'changeme'))

# Logging
handler = logging.FileHandler(os.path.join(cfg['output_dir'], 'webui.log'))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ScanForm(FlaskForm):
    bssid = StringField('BSSID', validators=[
        DataRequired(),
        Regexp(r'^[0-9A-Fa-f:]{17}$', message="Invalid MAC format")
    ])
    channel = IntegerField('Channel', validators=[
        DataRequired(),
        NumberRange(min=1, max=165)
    ])

class DeauthForm(ScanForm):
    count = IntegerField('Count', default=10, validators=[NumberRange(min=1)])
    interval = IntegerField('Interval (ms)', validators=[NumberRange(min=0)])

class BruteForm(FlaskForm):
    capture = StringField('Capture File', validators=[DataRequired()])
    bssid = StringField('BSSID', validators=[
        DataRequired(),
        Regexp(r'^[0-9A-Fa-f:]{17}$')
    ])
    wordlist = StringField('Wordlist Path', validators=[DataRequired()])

# Authentication decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == USER and check_password_hash(PW_HASH, form.password.data):
            session['logged_in'] = True
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    form = ScanForm()
    if form.validate_on_submit():
        try:
            pcap = do_scan(cfg, argparse.Namespace(
                iface=cfg['interface'], bssid=form.bssid.data,
                channel=form.channel.data, timeout=None
            ))
            flash(f"Handshake captured: {pcap}", 'success')
        except Exception as e:
            app.logger.exception("Scan failed")
            flash(f"Scan error: {e}", 'error')
        return redirect(url_for('index'))
    return render_template('scan.html', form=form)

@app.route('/deauth', methods=['GET', 'POST'])
@login_required
def deauth():
    form = DeauthForm()
    if form.validate_on_submit():
        try:
            do_deauth(cfg, argparse.Namespace(
                iface=cfg['interface'], bssid=form.bssid.data,
                count=form.count.data, interval=form.interval.data,
                no_ignore_negative_one=False
            ))
            flash("Deauth attack completed", 'success')
        except Exception as e:
            app.logger.exception("Deauth failed")
            flash(f"Deauth error: {e}", 'error')
        return redirect(url_for('index'))
    return render_template('deauth.html', form=form)

@app.route('/brute', methods=['GET', 'POST'])
@login_required
def brute():
    form = BruteForm()
    if form.validate_on_submit():
        try:
            key = do_brute(cfg, argparse.Namespace(
                capture=form.capture.data, bssid=form.bssid.data,
                wordlist=form.wordlist.data, tool=None, timeout=None
            ))
            flash(f"Password cracked: {key}", 'success')
        except Exception as e:
            app.logger.exception("Brute-force failed")
            flash(f"Brute error: {e}", 'error')
        return redirect(url_for('index'))
    return render_template('brute.html', form=form)

# Static file serving
@app.route('/static/<path:filename>')
@login_required
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=cfg.get('web_port', 8080), debug=False)