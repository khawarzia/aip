from django.db import models
from django.contrib.auth.models import User

class inputdata(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    slug = models.SlugField(max_length = 50 , null = True)
    Property_Value = models.FloatField(default=0)
    Start_Month_of_Tool = models.CharField(max_length = 15)
    Start_Year_of_Tool = models.IntegerField(default=0)
    Amount_Owed_As_of_Start_of_Tool = models.FloatField(default=0)
    Current_Payment_for_Loan = models.FloatField(default=0)
    Frequency_of_Payment = models.CharField(max_length = 15)
    Current_Interest_rate = models.FloatField(default=0)
    Terms_of_Rate = models.IntegerField(default=30)
    APPROVED_AMOUNT = models.FloatField(default=0)
    CURRENT_OWED_ON_HELOC = models.FloatField(default=0)
    PROJECTED_INJECTION_TO_MORTGAGE = models.FloatField(default=0)
    RECURRING_INJECTION_AFTER_HELOC_REACHES_ZERO = models.FloatField(default=0)
    HELOC_INITIAL_INTEREST_RATE = models.FloatField(default=0)
    
    def __str__(self):
        return (self.slug)

class currentdebt(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    slug = models.SlugField(max_length = 50 , null = True)
    Type = models.CharField(max_length = 25)
    Owed = models.FloatField(default=0)
    As_Of = models.DateField(null = True)
    Payment = models.FloatField(default=0)
    Rate = models.FloatField(default=0)

    def __str__(self):
        return (self.slug)

class regularexpenseddata(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    slug = models.SlugField(max_length = 50 , null = True)
    Description = models.CharField(max_length = 25)
    Amount = models.FloatField(default=0)
    Frequency = models.CharField(max_length = 15)
    Start_Date = models.DateField(null = True)
    End_Date = models.DateField(null = True)

    def __str__(self):
        return (self.slug)

class regularincomedata(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    slug = models.SlugField(max_length = 50 , null = True)
    Description = models.CharField(max_length = 25)
    Amount = models.FloatField(default=0)
    Frequency = models.CharField(max_length = 15)
    Start_Date = models.DateField(null = True)
    End_Date = models.DateField(null = True)

    def __str__(self):
        return (self.slug)

class lumpsumexpense(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    slug = models.SlugField(max_length = 50 , null = True)
    Description = models.CharField(max_length = 25)
    Amount = models.FloatField(default=0)
    When_Expended = models.DateField(null = True)

    def __str__(self):
        return (self.slug)

class lumpsumincome(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE , null = True)
    slug = models.SlugField(max_length = 50 , null = True)
    Description = models.CharField(max_length = 25)
    Amount = models.FloatField(default=0)
    When_Injecting = models.DateField(null = True)

    def __str__(self):
        return (self.slug)