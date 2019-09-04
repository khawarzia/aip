from django.shortcuts import render,redirect
from .forms import entry,entrydetailform,currentdebtform,regularexpenseddataform,regularincomedataform,lumpsumexpenseform,lumpsumincomeform
from .models import inputdata as idata,currentdebt,regularexpenseddata,regularincomedata,lumpsumexpense,lumpsumincome
from django.forms.models import model_to_dict
import pandas as pd
from calendar import monthrange
import calendar
from dateutil import relativedelta
from datetime import date
import numpy as np
from login.models import infor
from django.contrib.auth.decorators import login_required

def work(request):
    print (request)
    template = 'index.html'
    if request.method == "POST":
        # Inputs
        endDatePrimaryLoanusingTool = None
        originalprincipal = float(request.POST['Mortgage_owed'])
        interestrate = float(request.POST['Interest_rate'])
        monthlyinstallment = float(request.POST['Monthly_installment'])
        Income = float(request.POST['Monthly_income'])
        Expense = float(request.POST['Monthly_expenses'])
        CurrentDebtExpenses = float(request.POST['Current_debt'])
        Loanperiod = int(request.POST['Loan_period'])
        
        CashFlowSummary = pd.read_csv("~/aip/aip/templates/OutputFormat.csv")
 
        CashFlowSummary.set_index('P&I & HELOC Details', inplace=True)
        LoanTermComparison = pd.DataFrame(columns=['Loan Type', 'Value', 'Years', 'Months', 'Interest Cost'])
        
        principal = originalprincipal
        ProjectedHELOCInjection = int(0.05*originalprincipal) 
        approvedAmountHELOC = int(ProjectedHELOCInjection*4.5) 
        HELOCinterestRate = 0.06 
        
        def trunc_datetime(someDate):
            return someDate.replace(day=1)
            
        def Amortization(amount, flag, date):
            if flag == 0:
                return([originalprincipal, 0.0])
            
            else:
                if calendar.isleap(date.year):
                    daysintheyear = float(366)
                else:
                    daysintheyear = float(365)
            
                daysinthemonth = monthrange(date.year, date.month)[1]
                interestpayment = (principal*interestrate*daysinthemonth/daysintheyear)
                principalPayment =  monthlyinstallment - interestpayment
                endingPrincipal = amount - principalPayment
                return([endingPrincipal, interestpayment])
        
        def HELOCInterestCalculator(Amount, date):
            if calendar.isleap(date.year):
                daysintheyear = float(366)
            else:
                daysintheyear = float(365)
            
            daysinthemonth = monthrange(date.year, date.month)[1]
        
            interest = (HELOCinterestRate/daysintheyear)*Amount*daysinthemonth
            return(interest)
            
        LumpsumIncome = 0 
        LumpsumExpenses = 0 
        
        startpoint = pd.datetime.now()
        endpoint = startpoint + pd.DateOffset(years = Loanperiod) 
        endpoint = endpoint + pd.DateOffset(months = 1)
        
        daterange = pd.date_range(start = startpoint.date(), end = endpoint.date(), freq ='M')
        count = 0
        prevColumnname = daterange[0].strftime('%b-%y')
        interestPrimaryLoan = 0
        interestPrimaryLoanuisngTool = 0
        HELOCInterestSum = 0
        prevstuff = daterange[0]
        
        for stuff in daterange:
            columnname = stuff.strftime('%b-%y')
            CashFlowSummary[columnname] = None
        
            updatedamount = round(Amortization(principal, count,  prevstuff)[0],2)
            interestPrimaryLoan = interestPrimaryLoan + round(Amortization(principal, count,  prevstuff)[1],2)
            principal = updatedamount
            if updatedamount < 0:
                updatedamount = 0
                
            CashFlowSummary.loc['Original P&I Loan Balance', columnname] = updatedamount
            
            if (updatedamount == 0) or (stuff == daterange[-1]):
                endDatePrimaryLoan = stuff
                break
            
            if count > 3 and CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname] == 0:
                prevstuff = stuff
                prevColumnname = columnname
                count = count + 1
                CashFlowSummary.loc['New P&I Loan Balance with Injections', columnname] = 0
                CashFlowSummary.loc['HELOC Opening Balance', columnname] = 0
                continue
            
            CashFlowSummary.loc['Original HELOC Credit Limit', columnname] = approvedAmountHELOC
            CashFlowSummary.loc['HELOC Interest Rate', columnname] = HELOCinterestRate
        
            CashFlowSummary.loc['Regular Income', columnname] = Income
            CashFlowSummary.loc['Lump Sum Income', columnname] = LumpsumIncome
            TotalIncome = round((Income + LumpsumIncome),2)
            CashFlowSummary.loc['TOTAL INCOME', columnname] = TotalIncome
        
            CashFlowSummary.loc['Regular Expenses', columnname] = Expense
            CashFlowSummary.loc['Lump Sum Expenses', columnname] = LumpsumExpenses
            CashFlowSummary.loc['Current Debt Expenses', columnname] = CurrentDebtExpenses
            CashFlowSummary.loc['P&I Loan Payment Expense', columnname] = monthlyinstallment
            TotalExpense = round((Expense + LumpsumExpenses + CurrentDebtExpenses + monthlyinstallment), 2)
            CashFlowSummary.loc['TOTAL EXPENSES', columnname] = TotalExpense
            CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', columnname] = 0
        
            if count == 0:
                HELOCOpeningBalance = ProjectedHELOCInjection
                PILoanBalancewithInjections = round((updatedamount-ProjectedHELOCInjection),2)
                CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', columnname] = HELOCOpeningBalance
            
            if count != 0:
                HELOCOpeningBalance = CashFlowSummary.loc['HELOC Closing Balance (Forecasted)', prevColumnname]
                if count == 1:
                    principalforPILoanBalance = CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname]
                if count != 1:
                    principalforPILoanBalance = CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname] - CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', prevColumnname]
                
                PILoanBalancewithInjections = round(Amortization(principalforPILoanBalance, count, stuff)[0],2) 
                interestPrimaryLoanuisngTool = interestPrimaryLoanuisngTool + round(Amortization(principalforPILoanBalance, count, stuff)[1],2)
                if HELOCOpeningBalance <= 3000:
                    prevsurplus = CashFlowSummary.loc['Surplus from checking (injected into P&I)', prevColumnname]
                    CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', columnname] = float((ProjectedHELOCInjection + HELOCOpeningBalance + prevsurplus))
                    HELOCOpeningBalance = ProjectedHELOCInjection
                    
            CashFlowSummary.loc['HELOC Opening Balance', columnname] = HELOCOpeningBalance
        
            if PILoanBalancewithInjections < 0:
                PILoanBalancewithInjections = 0

            surplus = TotalIncome - TotalExpense - HELOCOpeningBalance
            if surplus < 0:
                surplus = 0
        
            HELOCInteresttobeCalculatedon = HELOCOpeningBalance + TotalExpense - TotalIncome
            if surplus > 0:
                HELOCInterest = 0
            else:
                HELOCInterest = HELOCInterestCalculator(HELOCInteresttobeCalculatedon, stuff )
            CashFlowSummary.loc['HELOC Interest Paid', columnname] = round(HELOCInterest,2)
        
            HELOCInterestSum = HELOCInterestSum + round(HELOCInterest,2)
        
            HELOCReducedBy = TotalIncome - TotalExpense - round(HELOCInterest,2)-surplus
            CashFlowSummary.loc['HELOC Reduced by', columnname] = HELOCReducedBy
        
            CashFlowSummary.loc['HELOC Closing Balance (Forecasted)', columnname] = HELOCOpeningBalance - HELOCReducedBy

            CashFlowSummary.loc['New P&I Loan Balance with Injections', columnname] = PILoanBalancewithInjections
    
            CashFlowSummary.loc['HELOC Buffer Available', columnname] = approvedAmountHELOC - HELOCOpeningBalance
        
            CashFlowSummary.loc['Surplus from checking (injected into P&I)', columnname] = surplus
                
            if CashFlowSummary.loc['New P&I Loan Balance with Injections', columnname] == 0:
                endDatePrimaryLoanusingTool = stuff
            else:
                endDatePrimaryLoanusingTool = stuff
        
            prevstuff = stuff
            prevColumnname = columnname
            count = count + 1

        if endDatePrimaryLoanusingTool == None:
            context = {'form':form,'check':True,'message':'Values are not valid'}
            return render(request,template,context)
        
        MonthsforPrimaryLoan = relativedelta.relativedelta(endDatePrimaryLoan, startpoint.replace(day = 1))
        MonthsforPrimaryLoanusingTool = relativedelta.relativedelta(endDatePrimaryLoanusingTool, startpoint)

        HELOCPayoffMonth = endDatePrimaryLoanusingTool.strftime('%B')
        HELOCPayoffYear = endDatePrimaryLoanusingTool.strftime('%Y')

        LoanTermComparison = LoanTermComparison.append({'Loan Type': 'Primary Loan',   'Value': originalprincipal, 'Years': MonthsforPrimaryLoan.years, 'Months': MonthsforPrimaryLoan.months, 'Interest Cost': interestPrimaryLoan }, ignore_index=True)
        LoanTermComparison = LoanTermComparison.append({'Loan Type': 'Primary Loan Using Tool',   'Value': originalprincipal, 'Years': MonthsforPrimaryLoanusingTool.years, 'Months': MonthsforPrimaryLoanusingTool.months, 'Interest Cost': interestPrimaryLoanuisngTool }, ignore_index=True)
        LoanTermComparison = LoanTermComparison.append({'Loan Type': 'HELOC Payoff -> month+year', 'Years': HELOCPayoffYear, 'Months': HELOCPayoffMonth, 'Interest Cost': HELOCInterestSum }, ignore_index=True)

        cfs = {}
        a = CashFlowSummary.to_dict().items()
        for i,j in a:
            cfs['Month'] = i
            for k,l in j.items():
                cfs[k] = l
            break

        ltc = {}
        a = LoanTermComparison.to_dict().items()
        for i,j in a:
            ltc[i] = []
            for k,l in j.items():
                ltc[i].append(l)
        print (a)

        context1 = {'form':form,'a':cfs.items(),'b':ltc.items(),'check':False,'message':''}
        form = entry()
        return render(request,template,context1)
    context = {'form':form,'check':False,'message':''}
    return render(request,template,context)

def about(request):
    template = 'about.html'
    context = {}
    return render(request,template,context)

def contact(request):
    template = 'contact.html'
    context = {}
    return render(request,template,context)

def pricing(request):
    template = 'pricing.html'
    context = {}
    return render(request,template,context)

@login_required(login_url='/loggin')
def dashboard(request):
    template = 'base-dashboard.html'
    
    objslist = [idata,currentdebt,regularexpenseddata,regularincomedata,lumpsumexpense,lumpsumincome]
    data = []
    debt = []
    expense = []
    income = []
    lsexpense = []
    lsincome = []
    for i in range(0,6):
        for j in objslist[i].objects.all():
            if j.user == request.user:
                if i == 0:
                    data.append(model_to_dict(j))
                elif i == 1:
                    debt.append(model_to_dict(j))
                elif i == 2:
                    expense.append(model_to_dict(j))
                elif i == 3:
                    income.append(model_to_dict(j))
                elif i == 4:
                    lsexpense.append(model_to_dict(j))
                else:
                    lsincome.append(model_to_dict(j))

    context = {'data':data,'debt':debt,'expense':expense,'income':income,'lsexpense':lsexpense,'lsincome':lsincome,'info':infor.objects.get(user=request.user)}
    return render(request,template,context)

@login_required(login_url='/loggin')
def data(request):
    template = 'base-propertydetail.html'
    if request.method == 'POST':
        try:
            a = idata.objects.get(user=request.user)
            a.Property_Value = request.POST['Property_Value']
            a.Start_Month_of_Tool = request.POST['Start_Month_of_Tool']
            a.Start_Year_of_Tool = request.POST['Start_Year_of_Tool']
            a.Amount_Owed_As_of_Start_of_Tool = request.POST['Amount_Owed_As_of_Start_of_Tool']
            a.Current_Payment_for_Loan = request.POST['Current_Payment_for_Loan']
            a.Frequency_of_Payment = request.POST['Frequency_of_Payment']
            a.Current_Interest_rate = request.POST['Current_Interest_rate']
            a.APPROVED_AMOUNT = request.POST['APPROVED_AMOUNT']
            a.CURRENT_OWED_ON_HELOC = request.POST['CURRENT_OWED_ON_HELOC']
            a.PROJECTED_INJECTION_TO_MORTGAGE = request.POST['PROJECTED_INJECTION_TO_MORTGAGE']
            a.RECURRING_INJECTION_AFTER_HELOC_REACHES_ZERO = request.POST['RECURRING_INJECTION_AFTER_HELOC_REACHES_ZERO']
            a.HELOC_INITIAL_INTEREST_RATE = request.POST['HELOC_INITIAL_INTEREST_RATE']
            a.save()
        except:
            a = idata()
            a.user = request.user
            a.slug = str(request.user.username) + str(len(idata.objects.all()) + 1)
            a.Property_Value = request.POST['Property_Value']
            a.Start_Month_of_Tool = request.POST['Start_Month_of_Tool']
            a.Start_Year_of_Tool = request.POST['Start_Year_of_Tool']
            a.Amount_Owed_As_of_Start_of_Tool = request.POST['Amount_Owed_As_of_Start_of_Tool']
            a.Current_Payment_for_Loan = request.POST['Current_Payment_for_Loan']
            a.Frequency_of_Payment = request.POST['Frequency_of_Payment']
            a.Current_Interest_rate = request.POST['Current_Interest_rate']
            a.APPROVED_AMOUNT = request.POST['APPROVED_AMOUNT']
            a.CURRENT_OWED_ON_HELOC = request.POST['CURRENT_OWED_ON_HELOC']
            a.PROJECTED_INJECTION_TO_MORTGAGE = request.POST['PROJECTED_INJECTION_TO_MORTGAGE']
            a.RECURRING_INJECTION_AFTER_HELOC_REACHES_ZERO = request.POST['RECURRING_INJECTION_AFTER_HELOC_REACHES_ZERO']
            a.HELOC_INITIAL_INTEREST_RATE = request.POST['HELOC_INITIAL_INTEREST_RATE']
            a.save()
        return redirect('/main-data')
    datav = []
    data = []
    a = idata.objects.all()
    for i in a:
        if request.user == i.user:
            datav.append(model_to_dict(i).items())
    for i in datav:
        a = []
        count = 3
        for k,j in i:
            if count != 0:
                count = count - 1
                continue
            a.append((k,j))
        data.append(a)
    if len(data) > 0:
        context = {'data':data[len(data)-1],'a':True}
        return render(request,template,context)
    context = {'a':False,'c':range(0,12)}
    return render(request,template,context)

@login_required(login_url='/loggin')
def debt(request):
    template = 'base-currentdebt.html'
    if request.method == 'POST':
        a = currentdebt()
        a.user = request.user
        a.slug = str(request.user.username) + str(len(idata.objects.all()) + 1)
        a.Type = request.POST['Type']
        a.Owed = request.POST['Owed']
        a.As_Of = request.POST['As_Of']
        a.Payment = request.POST['Payment']
        a.Rate = request.POST['Rate']
        a.save()
        return redirect('/debt')
    datav = []
    data = []
    a = currentdebt.objects.all()
    for i in a:
        if request.user == i.user:
            datav.append(model_to_dict(i).items())
    for i in datav:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                if count == 1:
                    temp = k
                count = count - 1
                continue
            a.append(k)
        a.append(temp)
        data.append(a)
    context = {'data':data}
    return render(request,template,context)

@login_required(login_url='/loggin')
def expense(request):
    template = 'base-expense.html'
    if request.method == 'POST':
        a = regularexpenseddata()
        a.user = request.user
        a.slug = str(request.user.username) + str(len(regularexpenseddata.objects.all()) + 1)
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.Frequency = request.POST['Frequency']
        a.Start_Date = request.POST['Start_Date']
        a.End_Date = request.POST['End_Date']
        a.save()
        return redirect('/expense')
    datav = []
    data = []
    a = regularexpenseddata.objects.all()
    for i in a:
        if request.user == i.user:
            datav.append(model_to_dict(i).items())
    for i in datav:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                if count == 1:
                    temp = k
                count = count - 1
                continue
            a.append(k)
        a.append(temp)
        data.append(a)
    context = {'data':data}
    return render(request,template,context)

@login_required(login_url='/loggin')
def income(request):
    template = 'base-income.html'
    if request.method == 'POST':
        a = regularincomedata()
        a.user = request.user
        a.slug = str(request.user.username) + str(len(regularincomedata.objects.all()) + 1)
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.Frequency = request.POST['Frequency']
        a.Start_Date = request.POST['Start_Date']
        a.End_Date = request.POST['End_Date']
        a.save()
        return redirect('/income')
    datav = []
    data = []
    a = regularincomedata.objects.all()
    for i in a:
        if request.user == i.user:
            datav.append(model_to_dict(i).items())
    for i in datav:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                if count == 1:
                    temp = k
                count = count - 1
                continue
            a.append(k)
        a.append(temp)
        data.append(a)
    context = {'data':data}
    return render(request,template,context)

@login_required(login_url='/loggin')
def lsexpense(request):
    template = 'base-lsexpense.html'
    if request.method == 'POST':
        a = lumpsumexpense()
        a.user = request.user
        a.slug = str(request.user.username) + str(len(lumpsumexpense.objects.all()) + 1)
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.When_Expended = request.POST['When_Expended']
        a.save()
        return redirect('/lsexpense')
    datav = []
    data = []
    a = lumpsumexpense.objects.all()
    for i in a:
        if request.user == i.user:
            datav.append(model_to_dict(i).items())
    for i in datav:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                if count == 1:
                    temp = k
                count = count - 1
                continue
            a.append(k)
        a.append(temp)
        data.append(a)
    context = {'data':data}
    return render(request,template,context)
    
@login_required(login_url='/loggin')
def lsincome(request):
    template = 'base-lsincome.html'
    if request.method == 'POST':
        a = lumpsumincome()
        a.user = request.user
        a.slug = str(request.user.username) + str(len(lumpsumincome.objects.all()) + 1)
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.When_Injecting = request.POST['When_Injecting']
        a.save()
        return redirect('/lsincome')
    datav = []
    data = []
    a = lumpsumincome.objects.all()
    for i in a:
        if request.user == i.user:
            datav.append(model_to_dict(i).items())
    for i in datav:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                if count == 1:
                    temp = k
                count = count - 1
                continue
            a.append(k)
        a.append(temp)
        data.append(a)
    context = {'data':data}
    return render(request,template,context)

@login_required(login_url='/loggin')
def summary(request,select):
    template = 'base-summary.html'
    expirycheck(request.user)
    a = idata.objects.all()
    b = currentdebt.objects.all()
    c = regularexpenseddata.objects.all()
    d = regularincomedata.objects.all()
    e = lumpsumexpense.objects.all()
    f = lumpsumincome.objects.all()
    objslist = [a,b,c,d,e,f]
    data = []
    debt = []
    expense = []
    income = []
    lsexpense = []
    lsincome = []
    for i in range(0,6):
        for j in objslist[i]:
            if j.user == request.user:
                if i == 0:
                    data.append(model_to_dict(j).items())
                elif i == 1:
                    debt.append(model_to_dict(j).items())
                elif i == 2:
                    expense.append(model_to_dict(j).items())
                elif i == 3:
                    income.append(model_to_dict(j).items())
                elif i == 4:
                    lsexpense.append(model_to_dict(j).items())
                else:
                    lsincome.append(model_to_dict(j).items())

    datav = []
    debtv = []
    expensev = []
    incomev = []
    lsexpensev = []
    lsincomev = []
    if len(data) > 0:
        for i,j in data[len(data)-1]:
            datav.append((i,j))
    for i in debt:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                count = count - 1
                continue
            a.append(k)
        debtv.append(a)
    for i in expense:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                count = count - 1
                continue
            a.append(k)
        expensev.append(a)
    for i in income:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                count = count - 1
                continue
            a.append(k)
        incomev.append(a)
    for i in lsexpense:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                count = count - 1
                continue
            a.append(k)
        lsexpensev.append(a)
    for i in lsincome:
        a = []
        count = 3
        for j,k in i:
            if count != 0:
                count = count - 1
                continue
            a.append(k)
        lsincomev.append(a)        

    if len(income) == 0 and len(expense) == 0 and len(data) == 0:
        context = {'check':True,'message':'Kindly enter at least one income and expense and your property details before starting use of the tool.'}
        return render(request,template,context)

    print (incomev)
    print (expensev)

    inputdata = pd.DataFrame(columns=['INPUTS','Values'])
    for i in range(2,len(datav)):
        inputdata = inputdata.append({'INPUTS':datav[i][0],'Values':datav[i][1]},ignore_index=True)
    inputdata.set_index('INPUTS', inplace=True)

    currentDebt = pd.DataFrame(columns=['','Type','Owed','As_Of','Payment','Rate'])
    for i in range(0,len(debtv)-1):
        currentDebt = currentDebt.append({'':debtv[i][0],'Type':debtv[i][0],'Owed':debtv[i][1],'As_Of':pd.to_datetime(debtv[i][2].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce'),'Payment':debtv[i][3],'Rate':debtv[i][4]},ignore_index=True)  

    for item in currentDebt.index:
        counter = 0
        if currentDebt.loc[item, 'Rate'] < 0.0001:
            monthsinpaying = (currentDebt.loc[item, 'Owed'])/float(currentDebt.loc[item, 'Payment'])
            monthsinpaying = int(np.ceil(monthsinpaying))
            PaidoffDate = currentDebt.loc[item, 'As_Of'] + pd.DateOffset(months = monthsinpaying)
            currentDebt.loc[item, 'Paid off'] = PaidoffDate
            
        else:
            monthsinpaying = TimeCalculatorCreditCard(currentDebt.loc[item, 'Owed'], currentDebt.loc[item, 'Payment'], currentDebt.loc[item, 'Rate'], counter)
            PaidoffDate = currentDebt.loc[item, 'As_Of'] + pd.DateOffset(months = monthsinpaying)
            currentDebt.loc[item, 'Paid off'] = PaidoffDate
            
    regularExpenses = pd.DataFrame(columns=['Description','Type','Amount','Frequency','Start_Date','End_Date'])
    for i in range(0,len(expensev)-1):
        regularExpenses = regularExpenses.append({'Description':expensev[i][0],'Type':expensev[i][0],'Amount':expensev[i][1],'Frequency':expensev[i][2],'Start_Date':pd.to_datetime(expensev[i][3].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce'),'End_Date':pd.to_datetime(expensev[i][4].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce')},ignore_index=True)
    regularExpenses['Amount'] = regularExpenses['Amount'].fillna(0)

    regularIncome = pd.DataFrame(columns=['Description','Type','Amount','Frequency','Start_Date','End_Date'])
    for i in range(0,len(incomev)-1):
        regularIncome = regularIncome.append({'Description':incomev[i][0],'Type':incomev[i][0],'Amount':incomev[i][1],'Frequency':incomev[i][2],'Start_Date':pd.to_datetime(incomev[i][3].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce'),'End_Date':pd.to_datetime(incomev[i][4].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce')},ignore_index=True)
    regularIncome['Amount'] = regularIncome['Amount'].fillna(0)

    LumpSumIncomedf = pd.DataFrame(columns=['Description','Amount','When_Injecting'])
    for i in range(0,len(lsincomev)-1):
        LumpSumIncomedf = LumpSumIncomedf.append({'Description':lsincomev[i][0],'Amount':lsincomev[i][1],'When_Injecting':pd.to_datetime(lsincomev[i][2].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce')},ignore_index=True)
    LumpSumIncomedf['Amount'] = LumpSumIncomedf['Amount'].fillna(0)

    LumpSumExpensesdf = pd.DataFrame(columns=['Description','Amount','When_Expended'])
    for i in range(0,len(lsexpensev)-1):
        LumpSumExpensesdf = LumpSumExpensesdf.append({'Description':lsexpensev[i][0],'Amount':lsexpensev[i][1],'When_Expended':pd.to_datetime(lsexpensev[i][2].strftime(format = '%m-%d-%y'),format = '%m-%d-%y',errors='coerce')},ignore_index=True)
    LumpSumExpensesdf['Amount'] = LumpSumExpensesdf['Amount'].fillna(0)

    groupobj_income = regularIncome.groupby(['Frequency', 'Description', 'Start_Date'])
    groupobj_expenses = regularExpenses.groupby(['Frequency', 'Description', 'Start_Date']) 

    #OuputDataFormat
    CashFlowSummary = pd.read_csv('~/aip/aip/templates/OutputFormat1.csv')
    CashFlowSummary.set_index('P&I & HELOC Details', inplace=True)
    YearlyBalances = pd.DataFrame(columns=['Date', 'Original P&I Loan', 'HELOC', 'P&I with Injections'])
    LoanTermComparison = pd.DataFrame(columns=['Loan Type', 'Value', 'Years', 'Months', 'Interest Cost'])

    originalprincipal = float(inputdata.loc['Amount_Owed_As_of_Start_of_Tool'])
    principal = originalprincipal
    interestrate = float(inputdata.loc['Current_Interest_rate'])/100
    monthlyinstallment = float(inputdata.loc['Current_Payment_for_Loan'])
    approvedAmountHELOC = float(inputdata.loc['APPROVED_AMOUNT'])
    HELOCinterestRate = float(inputdata.loc['HELOC_INITIAL_INTEREST_RATE'])/100
    ProjectedHELOCInjection = float(inputdata.loc['PROJECTED_INJECTION_TO_MORTGAGE'])
    CurrentOwedonHeloc = float(inputdata.loc['CURRENT_OWED_ON_HELOC'])
    
    def trunc_datetime(someDate):
        return someDate.replace(day=1)
        
    def Amortization(amount, flag, date):
        if flag == 0:
            return([originalprincipal, 0.0])
        
        else:
            if calendar.isleap(date.year):
                daysintheyear = float(366)
            else:
                daysintheyear = float(365)
        
            daysinthemonth = monthrange(date.year, date.month)[1]
            interestpayment = (principal*interestrate*daysinthemonth/daysintheyear)
            principalPayment =  monthlyinstallment - interestpayment
            endingPrincipal = amount - principalPayment
            return([endingPrincipal, interestpayment])
            
    def Income_Calculator(date):
        income_monthly = 0
        income_onetime = 0
        income_yearly = 0
        for group in groupobj_income:
            if group[0][0] == 'Monthly':
                parameter = trunc_datetime(group[1]['Start_Date'].tolist()[0]) <= trunc_datetime(date) <= trunc_datetime(group[1]['End_Date'].tolist()[0])
                if(parameter == True):
                    income_monthly = income_monthly + float(group[1]['Amount'].tolist()[0])
                
            if group[0][0] == 'One Time':                
                parameter = ((trunc_datetime(group[1]['Start_Date'].tolist()[0]) <= trunc_datetime(date) <= trunc_datetime(group[1]['End_Date'].tolist()[0]))
                                & (date.month == group[1]['Start_Date'].tolist()[0].month))
                if(parameter == True):
                    income_onetime = income_onetime + float(group[1]['Amount'].tolist()[0])               
        
            if group[0][0] == 'Yearly':
                parameter = ((trunc_datetime(group[1]['Start_Date'].tolist()[0]) <= trunc_datetime(date) <= trunc_datetime(group[1]['End_Date'].tolist()[0]))
                                & (date.month == group[1]['Start_Date'].tolist()[0].month))
                if(parameter == True):
                    income_yearly = income_yearly + float(group[1]['Amount'].tolist()[0])
                    
        TotalIncome = income_monthly + income_yearly + income_onetime
        return(TotalIncome)
        
        
    def Expense_Calculator(date):
        expense_monthly = 0
        expense_onetime = 0
        expense_yearly = 0
        for group in groupobj_expenses:
            if group[0][0] == 'Monthly':
                parameter = trunc_datetime(group[1]['Start_Date'].tolist()[0]) <= trunc_datetime(date) <= trunc_datetime(group[1]['End_Date'].tolist()[0])
                if(parameter == True):
                    expense_monthly = expense_monthly + float(sum(group[1]['Amount'].tolist()))
                
            if group[0][0] == 'One Time':                
                parameter = ((trunc_datetime(group[1]['Start_Date'].tolist()[0]) <= trunc_datetime(date) <= trunc_datetime(group[1]['End_Date'].tolist()[0]))
                                & (date.month == group[1]['Start_Date'].tolist()[0].month))
                if(parameter == True):
                    expense_onetime = expense_onetime + float(sum(group[1]['Amount'].tolist()))               
        
            if group[0][0] == 'Yearly':
                parameter = ((trunc_datetime(group[1]['Start_Date'].tolist()[0]) <= trunc_datetime(date) <= trunc_datetime(group[1]['End_Date'].tolist()[0]))
                                & (date.month == group[1]['Start_Date'].tolist()[0].month))
                if(parameter == True):
                    expense_yearly = expense_yearly + float(sum(group[1]['Amount'].tolist()))
                
    
        TotalExpense = expense_monthly + expense_yearly + expense_onetime
        return(TotalExpense)
    
      
    def Debt_Calculator(date):
        sumDebt = 0
        for item in currentDebt.index:
            parameter = trunc_datetime(currentDebt.loc[item, 'As_Of']) <= trunc_datetime(date) <= trunc_datetime(currentDebt.loc[item, 'Paid off'])
            if parameter == True:
                sumDebt = sumDebt + currentDebt.loc[item, 'Payment']
            
        return(sumDebt)
    
    def HELOCInterestCalculator(Amount, date):
        if calendar.isleap(date.year):
            daysintheyear = float(366)
        else:
            daysintheyear = float(365)
        
        daysinthemonth = monthrange(date.year, date.month)[1]
    
        interest = (HELOCinterestRate/daysintheyear)*Amount*daysinthemonth
        return(interest)
        
    def LumpSumIncomeCalculator(date):
        LumpSumIncome = 0
        if LumpSumIncomedf.index.size == 0:
            return(LumpSumIncome)
        
        else:
            for item in LumpSumIncomedf.index:
                parameter = trunc_datetime(LumpSumIncomedf.loc[item, 'When_Injecting']) == trunc_datetime(date)
                if parameter == True:
                    LumpSumIncome = LumpSumIncome + LumpSumIncomedf.loc[item, 'Amount']
            
            return(LumpSumIncome)
    
    def LumpSumExpensesCalculator(date):
        LumpSumExpenses = 0
    
        if LumpSumExpensesdf.index.size == 0:
            return(LumpSumExpenses)
        
        else:
            for item in LumpSumExpensesdf.index:
                parameter = trunc_datetime(LumpSumExpensesdf.loc[item, 'When_Expended']) == trunc_datetime(date)
                if parameter == True:
                    LumpSumExpenses = LumpSumExpenses + LumpSumExpensesdf.loc[item, 'Amount']
            
            return(LumpSumExpenses)
    
    startpoint = pd.datetime.now()
    Loanperiod = int(inputdata.loc['Terms_of_Rate'])
    endpoint = startpoint + pd.DateOffset(years = Loanperiod) 
    endpoint = endpoint + pd.DateOffset(months = 1)
    
    daterange = pd.date_range(start = startpoint.date(), end = endpoint.date(), freq ='M')
    count = 0
    prevColumnname = daterange[0].strftime('%b-%y')
    interestPrimaryLoan = 0
    interestPrimaryLoanuisngTool = 0
    HELOCInterestSum = 0
    prevstuff = daterange[0]
    endDatePrimaryLoanusingTool = None
    
    for stuff in daterange:
        columnname = stuff.strftime('%b-%y')
        CashFlowSummary[columnname] = None
    
        updatedamount = round(Amortization(principal, count,  prevstuff)[0],2)
        interestPrimaryLoan = interestPrimaryLoan + round(Amortization(principal, count,  prevstuff)[1],2)
        principal = updatedamount
        if updatedamount < 0:
            updatedamount = 0
            
        CashFlowSummary.loc['Original P&I Loan Balance', columnname] = updatedamount
        
        if stuff.month == 2:
            YearlyBalances = YearlyBalances.append({'Date': 'January-' + str(stuff.year), 'Original P&I Loan' : CashFlowSummary.loc['Original P&I Loan Balance', prevColumnname], 'HELOC': CashFlowSummary.loc['HELOC Opening Balance', prevColumnname], 'P&I with Injections': CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname]}, ignore_index=True)
       
        if (updatedamount == 0) or (stuff == daterange[-1]):
            endDatePrimaryLoan = stuff
            break
        
        if count > 3 and CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname] == 0:
            prevstuff = stuff
            prevColumnname = columnname
            count = count + 1
            CashFlowSummary.loc['New P&I Loan Balance with Injections', columnname] = 0
            CashFlowSummary.loc['HELOC Opening Balance', columnname] = 0
            continue
        
        CashFlowSummary.loc['Original HELOC Credit Limit', columnname] = approvedAmountHELOC
        CashFlowSummary.loc['HELOC Interest Rate', columnname] = HELOCinterestRate
    
        Income = Income_Calculator(stuff)
        CashFlowSummary.loc['Regular Income', columnname] = Income
        LumpsumIncome = float(LumpSumIncomeCalculator(stuff))
        CashFlowSummary.loc['Lump Sum Income', columnname] = LumpsumIncome
        TotalIncome = round((Income + LumpsumIncome),2)
        CashFlowSummary.loc['TOTAL INCOME', columnname] = TotalIncome
    
        Expense = Expense_Calculator(stuff)
        CashFlowSummary.loc['Regular Expenses', columnname] = Expense
        LumpsumExpenses = float(LumpSumExpensesCalculator(stuff))
        CashFlowSummary.loc['Lump Sum Expenses', columnname] = LumpsumExpenses
        CurrentDebtExpenses = Debt_Calculator(stuff)
        CashFlowSummary.loc['Current Debt Expenses', columnname] = CurrentDebtExpenses
        CashFlowSummary.loc['P&I Loan Payment Expense', columnname] = monthlyinstallment
        TotalExpense = round((Expense + LumpsumExpenses + CurrentDebtExpenses + monthlyinstallment), 2)
        CashFlowSummary.loc['TOTAL EXPENSES', columnname] = TotalExpense
        CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', columnname] = 0
    
        if count == 0:
            HELOCOpeningBalance = ProjectedHELOCInjection + CurrentOwedonHeloc
            PILoanBalancewithInjections = round((updatedamount-ProjectedHELOCInjection),2)
            CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', columnname] = HELOCOpeningBalance
          
        if count != 0:
            HELOCOpeningBalance = CashFlowSummary.loc['HELOC Closing Balance (Forecasted)', prevColumnname]
            if count == 1:
                principalforPILoanBalance = CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname]
            if count != 1:
                principalforPILoanBalance = CashFlowSummary.loc['New P&I Loan Balance with Injections', prevColumnname] - CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', prevColumnname]
            
            PILoanBalancewithInjections = round(Amortization(principalforPILoanBalance, count, stuff)[0],2) 
            interestPrimaryLoanuisngTool = interestPrimaryLoanuisngTool + round(Amortization(principalforPILoanBalance, count, stuff)[1],2)
            if HELOCOpeningBalance <= 3000:
                prevsurplus = CashFlowSummary.loc['Surplus from checking (injected into P&I)', prevColumnname]
                CashFlowSummary.loc['PROJECTED INJECTION TO MORTGAGE', columnname] = float((ProjectedHELOCInjection + HELOCOpeningBalance + prevsurplus))
                HELOCOpeningBalance = ProjectedHELOCInjection
                
        CashFlowSummary.loc['HELOC Opening Balance', columnname] = HELOCOpeningBalance
    
        if PILoanBalancewithInjections < 0:
            PILoanBalancewithInjections = 0

        surplus = TotalIncome - TotalExpense - HELOCOpeningBalance
        if surplus < 0:
            surplus = 0
    
        HELOCInteresttobeCalculatedon = HELOCOpeningBalance + TotalExpense - TotalIncome
        if surplus > 0:
            HELOCInterest = 0
        else:
            HELOCInterest = HELOCInterestCalculator(HELOCInteresttobeCalculatedon, stuff )
        CashFlowSummary.loc['HELOC Interest Paid', columnname] = round(HELOCInterest,2)
    
        HELOCInterestSum = HELOCInterestSum + round(HELOCInterest,2)
     
        HELOCReducedBy = TotalIncome - TotalExpense - round(HELOCInterest,2)-surplus
        CashFlowSummary.loc['HELOC Reduced by', columnname] = HELOCReducedBy
    
        CashFlowSummary.loc['HELOC Closing Balance (Forecasted)', columnname] = HELOCOpeningBalance - HELOCReducedBy

        CashFlowSummary.loc['New P&I Loan Balance with Injections', columnname] = PILoanBalancewithInjections
  
        CashFlowSummary.loc['HELOC Buffer Available', columnname] = approvedAmountHELOC - HELOCOpeningBalance
    
        CashFlowSummary.loc['Surplus from checking (injected into P&I)', columnname] = surplus
            
        if CashFlowSummary.loc['New P&I Loan Balance with Injections', columnname] == 0:
            endDatePrimaryLoanusingTool = stuff
    
        prevstuff = stuff
        prevColumnname = columnname
        count = count + 1
       
    MonthsforPrimaryLoan = relativedelta.relativedelta(endDatePrimaryLoan, startpoint.replace(day = 1))
    MonthsforPrimaryLoanusingTool = relativedelta.relativedelta(endDatePrimaryLoanusingTool, startpoint)

    HELOCPayoffMonth = endDatePrimaryLoanusingTool.strftime('%B')
    HELOCPayoffYear = endDatePrimaryLoanusingTool.strftime('%Y')

    LoanTermComparison = LoanTermComparison.append({'Loan Type': 'Primary Loan',   'Value': originalprincipal, 'Years': MonthsforPrimaryLoan.years, 'Months': MonthsforPrimaryLoan.months, 'Interest Cost': interestPrimaryLoan }, ignore_index=True)
    LoanTermComparison = LoanTermComparison.append({'Loan Type': 'Primary Loan Using Tool',   'Value': originalprincipal, 'Years': MonthsforPrimaryLoanusingTool.years, 'Months': MonthsforPrimaryLoanusingTool.months, 'Interest Cost': interestPrimaryLoanuisngTool }, ignore_index=True)
    LoanTermComparison = LoanTermComparison.append({'Loan Type': 'HELOC Payoff -> month+year', 'Years': HELOCPayoffYear, 'Months': HELOCPayoffMonth, 'Interest Cost': HELOCInterestSum }, ignore_index=True)
    
    use = infor.objects.get(user = request.user)
    count = 0
    cfs = {}
    a = CashFlowSummary.to_dict().items()
    for i,j in a:
        cfs[i] = {}
        count += 1
        for k,l in j.items():
            cfs[i][k] = l
        if count == 1 and use.package == 'Starter   Free':
            break
        if count == 3 and use.package == 'Gold   $29.99':
            break

    yb = {}
    a = YearlyBalances.to_dict().items()
    for i,j in a:
        yb[i] = []
        for k,l in j.items():
            yb[i].append(l)

    ltc = {}
    a = LoanTermComparison.to_dict().items()
    for i,j in a:
        ltc[i] = []
        for k,l in j.items():
            ltc[i].append(l)

    context = {'check':False,'message':'','cfs':cfs.items(),'yb':yb.items(),'ltc':ltc.items(),'select':select}
    return render(request,template,context)

def delete(request,model,the_slug):
    if str(model) == '1':
        currentdebt.objects.get(slug=the_slug).delete()
        return redirect('/debt')
    elif str(model) == '2':
        regularexpensedata.objects.get(slug=the_slug).delete()
        return redirect('/expense')
    elif str(model) == '3':
        regularincomedata.objects.get(slug=the_slug).delete()
        return redirect('/income')
    elif str(model) == '4':
        lumpsumexpense.objects.get(slug=the_slug).delete()
        return redirect('/lsexpense')
    else:
        lumpsumincome.objects.get(slug=the_slug).delete()
        return redirect('/lsincome')

def edit(request,model):
    if str(model) == '1':
        a = currentdebt.objects.get(slug=request.POST['slug'])
        a.Type = request.POST['Type']
        a.Owed = request.POST['Owed']
        a.As_Of = request.POST['As_Of']
        a.Payment = request.POST['Payment']
        a.Rate = request.POST['Rate']
        a.save()
        return redirect('/debt')
    elif str(model) == '2':
        a = regularexpenseddata.objects.get(slug=request.POST['slug'])
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.Frequency = request.POST['Frequency']
        a.Start_Date = request.POST['Start_Date']
        a.End_Date = request.POST['End_Date']
        a.save()
        return redirect('/expense')
    elif str(model) == '3':
        a = regularincomedata.objects.get(slug=request.POST['slug'])
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.Frequency = request.POST['Frequency']
        a.Start_Date = request.POST['Start_Date']
        a.End_Date = request.POST['End_Date']
        a.save()
        return redirect('/income')
    elif str(model) == '4':
        a = lumpsumexpense.objects.get(slug=request.POST['slug'])
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.When_Expended = request.POST['When_Expended']
        a.save()
        return redirect('/lsexpense')
    else:
        a = lumpsumincome.objects.get(slug=request.POST['slug'])
        a.Description = request.POST['Description']
        a.Amount = request.POST['Amount']
        a.When_Expended = request.POST['When_Injecting']
        a.save()
        return redirect('/lsincome')

def expirycheck(name):
    infors = infor.objects.all()
    for i in infors:
        if name == i.user:
            d1 = i.end
            d2 = date.today()
            if d1 <= d2:
                i.started = False
                i.save()
                redirect('/confirm')
    return

def TimeCalculatorCreditCard(AmountOwed, Payment, Rate, counter):
    interest = (AmountOwed*Rate)/12
    PrincipalPayment = Payment - interest
    Endingprincipal = AmountOwed - PrincipalPayment
    counter = counter + 1
    if Endingprincipal == 0 or Endingprincipal < 0:
        return(counter)
    else:
        return(TimeCalculatorCreditCard(Endingprincipal, Payment, Rate, counter))  
