import uuid
from django.db import models
from consultations.models import consultations
from patients.models import SpravochnikSpecialistov

class Srochnost(models.TextChoices):
    EKSTRENNO = "Экстренно", "Экстренно"
    SROCHNO = "Срочно", "Срочно"
    PLANOVO = "Планово", "Планово"
    SAMOPOMOSHCH = "Самопомощь", "Самопомощь"

class RezultatyMarshrutizatsii(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessiya = models.ForeignKey(consultations, on_delete=models.CASCADE, db_column="sessiya")
    srochnost = models.CharField(max_length=50, choices=Srochnost.choices, blank=True, null=True)
    specialist = models.ForeignKey(SpravochnikSpecialistov, on_delete=models.SET_NULL, blank=True, null=True, db_column="specialist")
    obosnovaniye = models.BinaryField(blank=True, null=True)
    rekomendatsii = models.BinaryField(blank=True, null=True)
    data_sozdaniya = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rezultaty_marshrutizatsii"
        managed = False