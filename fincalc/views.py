from pdb import post_mortem
from flask import Blueprint, g, flash, redirect, render_template, request, url_for

bp = Blueprint('views', __name__)

@bp.route('/', methods=('GET','POST'))
def index():
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
            return redirect(url_for('views.index'))
        else:
            if float(request.form['loanAmount']) == 0:
                error = "Your loan amount must be greater than 0."
                flash(error)
                return redirect(url_for('views.index'))
            loan_amount = float(request.form['loanAmount'])
            if float(request.form['interestRate']) == 0:
                error = "Your interest rate not be equal to 0."
                flash(error)
                return redirect(url_for('views.index'))
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
                return redirect(url_for('views.index'))
            else:     
                total_months = (years * 12) + months
                loan_details = loan_calculator(loan_amount, interest_rate, pay_frequency, total_months)
                submit = True 
                
                if 'reset' in request.form:
                    submit = False 
                print(submit)
                return render_template('index.html', LOAN_DETAILS = loan_details, SUBMIT = submit)

    return render_template('index.html', SUBMIT = False)


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

