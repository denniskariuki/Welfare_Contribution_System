from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ContributionForm(FlaskForm):
    amount = DecimalField('Amount (KES)', validators=[DataRequired()])
    description = TextAreaField('Description (Optional)')
    submit = SubmitField('Contribute')

class WithdrawalRequestForm(FlaskForm):
    amount = DecimalField('Amount (KES)', validators=[DataRequired()])
    reason = TextAreaField('Reason for Withdrawal', validators=[DataRequired()])
    submit = SubmitField('Request Withdrawal')

class ApproveWithdrawalForm(FlaskForm):
    notes = TextAreaField('Admin Notes')
    submit = SubmitField('Approve')

class RejectWithdrawalForm(FlaskForm):
    notes = TextAreaField('Reason for Rejection')
    submit = SubmitField('Reject')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Save Changes')