from django import forms
from first import settings

frequency_values = [
    ('One Time','One Time'),
    ('Monthly','Monthly'),
    ('Yearly','Yearly'),
]

months = [
    ('January','January'),
    ('February','February'),
    ('March','March'),
    ('April','April'),
    ('May','May'),
    ('June','June'),
    ('July','July'),
    ('August','August'),
    ('September','September'),
    ('October','October'),
    ('November','November'),
    ('December','December'),
]

class entry(forms.Form):
    Mortgage_owed = forms.FloatField()
    Interest_rate = forms.FloatField()
    Monthly_installment = forms.FloatField()
    Monthly_income = forms.FloatField()
    Monthly_expenses = forms.FloatField()
    Current_debt = forms.FloatField()
    Loan_period = forms.IntegerField()

class entrydetailform(forms.Form):
    Property_Value = forms.FloatField()
    Start_Month_of_Tool = forms.ChoiceField(choices=months, widget=forms.Select)
    Start_Year_of_Tool = forms.IntegerField()
    Amount_Owed_As_of_Start_of_Tool = forms.FloatField()
    Current_Payment_for_Loan = forms.FloatField()
    Frequency_of_Payment = forms.ChoiceField(choices=frequency_values, widget=forms.Select)
    Current_Interest_rate = forms.FloatField()
    Terms_of_Rate = forms.IntegerField()
    APPROVED_AMOUNT = forms.FloatField()
    CURRENT_OWED_ON_HELOC = forms.FloatField()
    PROJECTED_INJECTION_TO_MORTGAGE = forms.FloatField()
    RECURRING_INJECTION_AFTER_HELOC_REACHES_ZERO = forms.FloatField()
    HELOC_INITIAL_INTEREST_RATE = forms.FloatField()

class currentdebtform(forms.Form):
    Type = forms.CharField()
    Owed = forms.FloatField()
    As_Of = forms.DateField(widget=forms.SelectDateWidget)
    Payment = forms.FloatField()
    Rate = forms.FloatField()

class regularexpenseddataform(forms.Form):
    Description = forms.CharField()
    Amount = forms.FloatField()
    Frequency = forms.ChoiceField(choices=frequency_values, widget=forms.Select)
    Start_Date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000,2100)))
    End_Date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000,2100)))

class regularincomedataform(forms.Form):
    Description = forms.CharField()
    Amount = forms.FloatField()
    Frequency = forms.ChoiceField(choices=frequency_values, widget=forms.Select)
    Start_Date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000,2100)))
    End_Date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000,2100)))

class lumpsumexpenseform(forms.Form):
    Description = forms.CharField()
    Amount = forms.FloatField()
    When_Expended = forms.DateField(widget=forms.SelectDateWidget)

class lumpsumincomeform(forms.Form):
    Description = forms.CharField()
    Amount = forms.FloatField()
    When_Injecting = forms.DateField(widget=forms.SelectDateWidget)