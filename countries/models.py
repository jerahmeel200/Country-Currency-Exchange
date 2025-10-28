from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=200, unique=True, db_index=True)
    capital = models.CharField(max_length=200, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.FloatField(null=True, blank=True)
    estimated_gdp = models.FloatField(null=True, blank=True)
    flag_url = models.URLField(max_length=500, null=True, blank=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class RefreshStatus(models.Model):
    # only one row expected; used to track last refresh timestamp and total
    last_refreshed_at = models.DateTimeField(null=True, blank=True)
    total_countries  = models.IntegerField(default=0) 


    class Meta:
        verbose_name = "Refresh Status"
        verbose_name_plural = "Refresh Status"

        def __str__(self):
            return f"Refreshed at {self.last_refreshed_at} ({self.total_countries})"
