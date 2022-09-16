from flask import Blueprint, g, flash, redirect, render_template, request, url_for

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    return render_template('index.html')
