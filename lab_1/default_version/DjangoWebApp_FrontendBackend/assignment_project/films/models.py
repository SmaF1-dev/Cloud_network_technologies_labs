from django.db import models

# Create your models here.
class Language(models.Model):
    language_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'language'

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'

class Actor(models.Model):
    actor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'actor'

class Film(models.Model):
    film_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='films')
    rental_duration = models.IntegerField()
    rental_rate = models.DecimalField(max_digits=4, decimal_places=2)
    length = models.IntegerField(null=True, blank=True)
    replacement_cost = models.DecimalField(max_digits=5, decimal_places=2)
    rating = models.CharField(max_length=10, null=True, blank=True)
    special_features = models.TextField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'film'

class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    store_id = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'

class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    manager_staff_id = models.IntegerField()
    address_id = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store'

class Rental(models.Model):
    rental_id = models.AutoField(primary_key=True)
    rental_date = models.DateTimeField()
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    customer_id = models.IntegerField()
    return_date = models.DateTimeField(null=True, blank=True)
    staff_id = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rental'

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField()
    staff_id = models.IntegerField()
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateTimeField()
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment'

class FilmActor(models.Model):
    film_id = models.ForeignKey(Film, on_delete=models.CASCADE)
    actor_id = models.ForeignKey(Actor, on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'film_actor'

class FilmCategory(models.Model):
    film_id = models.ForeignKey(Film, on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'film_category'
