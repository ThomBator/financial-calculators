import base64
from io import BytesIO
from matplotlib.figure import Figure
import seaborn as sns
from pdb import post_mortem
from flask import Blueprint, g, flash, redirect, render_template, request, url_for

bp = Blueprint('views', __name__)

@bp.route('/', methods=('GET','POST'))
def index():
    return render_template('index.html')

@bp.route('/loan', methods=('GET', 'POST'))
def loan():
    if request.method == 'POST':
        error = None 
        if not request.form['loanAmount']:
            error = "Loan amount is required"
        elif not request.form['years'] and not request.form['months']:
            error = "You must enter a minimum of 1 month or 1 year."
        elif not request.form['interestRate']:
            error = "Please enter your interest rate pecentage"
        elif not request.form['payFrequency']:
            error = "Please select your payment frequency"
        if error is not None: 
            flash(error)
            return redirect(url_for('views.loan'))
        else:
            if float(request.form['loanAmount']) == 0:
                error = "Your loan amount must be greater than 0."
                flash(error)
                return redirect(url_for('views.loan'))
            else:
                loan_amount = float(request.form['loanAmount'])
            if float(request.form['interestRate']) == 0:
                error = "Your interest rate not be equal to 0."
                flash(error)
                return redirect(url_for('views.loan'))
            else:
                interest_rate = float(request.form['interestRate'])
            if len(request.form['years']) == 0:
                years = 0 
            else: 
                years = int(request.form['years'])
            if len(request.form['months']) == 0:
                months = 0 
            else: 
                months = int(request.form['months']) 
            pay_frequency = request.form['payFrequency']
            if months == 0  and years == 0:
                error = "You have entered 0 for both month and year. Please enter a value greater than 0 for at least one category."
                flash(error)
                return redirect(url_for('views.loan'))
            else:     
                total_months = (years * 12) + months
                loan_details = loan_calculator(loan_amount, interest_rate, pay_frequency, total_months)
                submit = True 
                loan_chart = make_chart(loan_amount, float(loan_details["interest_paid"]))
                if 'reset' in request.form:
                    return redirect(url_for('views.loan'))                
                return render_template('loan.html', LOAN_DETAILS = loan_details, SUBMIT = submit, LOAN_CHART = loan_chart)

    return render_template('loan.html', SUBMIT = False)



@bp.route('/invest', methods=('POST','GET'))
def invest():
    return render_template('invest.html')

def loan_calculator(loan_amount: float, interest_rate: float, pay_frequency: str, total_months: int) -> dict: 
    if pay_frequency == 'monthly':
        period_interest = interest_rate / 1200 
        total_periods = total_months
    elif pay_frequency == 'bi-weekly':
        period_interest = interest_rate /2600
        total_periods = (total_months / 12) * 26
    else:
        period_interest = interest_rate / 5200
        total_periods = (total_months / 12) * 52  
   

    total_loan_cost = (
        (loan_amount * period_interest * total_periods)
        /(1-(pow(1+ period_interest, -total_periods)))
    )
    
    period_payment = round(total_loan_cost / total_periods, 2)
    interest_paid = round(total_loan_cost - loan_amount,2)  
    total_loan_cost = round(total_loan_cost, 2) 
    total_loan_str = "{:.2f}".format(total_loan_cost) 
    period_payment_str = "{:.2f}".format(period_payment)
    interest_paid_str =  "{:.2f}".format(interest_paid)

    loan_details = {"total_loan_cost": total_loan_str, "period_payment": period_payment_str, "interest_paid": interest_paid_str, "period_type": pay_frequency}
    return loan_details 

def make_chart(total_loan : float, interest_paid: float):
    
    pie_list = [total_loan, interest_paid] #list of values for pie chart
    pie_labels = ["Principal", "Interest"]
    colors = sns.color_palette("Paired")[0:2]
    fig = Figure() 
    ax = fig.subplots()
    fig.set_facecolor("#f9f8f7")
    ax.pie(pie_list, labels=pie_labels,colors = colors, autopct='%.1f%%', explode = [0, .025], )
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data

