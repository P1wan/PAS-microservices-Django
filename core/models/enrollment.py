"""Modelos de matrícula corrigidos conforme exigência do professor."""

from django.db import models
from django.core.exceptions import ValidationError
from .academic import Discente, Disciplina, Livro


class Matricula(models.Model):
    """Uma matrícula que agrupa múltiplas disciplinas.

    Uma matrícula tem um ID único e pode conter várias disciplinas.
    O professor exige que disciplinas sejam adicionadas/removidas
    da MESMA matrícula, não criando novos IDs.
    """
    discente = models.ForeignKey(
        Discente,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )
    periodo = models.CharField(
        max_length=20,
        help_text="Ex: 2024.2, 2025.1"
    )
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'

    def __str__(self):
        status = "ativa" if self.ativa else "inativa"
        qtd = self.disciplinas_matricula.filter(ativa=True).count()
        return f"Matrícula #{self.id} - {self.discente.nome} ({qtd} disciplinas, {status})"

    def quantidade_disciplinas_ativas(self) -> int:
        """Retorna quantidade de disciplinas ativas nesta matrícula."""
        return self.disciplinas_matricula.filter(ativa=True).count()

    def clean(self):
        """Validações do modelo."""
        # Verificar se discente já tem matrícula ativa no período
        if self.ativa:
            existe = Matricula.objects.filter(
                discente=self.discente,
                periodo=self.periodo,
                ativa=True
            ).exclude(pk=self.pk).exists()

            if existe:
                raise ValidationError(
                    f"Discente já possui matrícula ativa no período {self.periodo}"
                )


class MatriculaDisciplina(models.Model):
    """Relacionamento entre Matrícula e Disciplina.

    Permite adicionar/remover disciplinas de uma matrícula existente.
    """
    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='disciplinas_matricula'
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='matriculas_disciplina'
    )
    adicionada_em = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ['-adicionada_em']
        unique_together = [['matricula', 'disciplina']]
        verbose_name = 'Disciplina da Matrícula'
        verbose_name_plural = 'Disciplinas das Matrículas'

    def __str__(self):
        status = "ativa" if self.ativa else "removida"
        return f"{self.disciplina.nome} ({status})"

    def clean(self):
        """Validações do modelo."""
        # Verificar se já existe (ativa ou não)
        if not self.pk:
            existe = MatriculaDisciplina.objects.filter(
                matricula=self.matricula,
                disciplina=self.disciplina,
            ).exists()

            if existe:
                raise ValidationError(
                    "Esta disciplina já foi adicionada a esta matrícula"
                )


class ReservaLivro(models.Model):
    """Reserva de livro por discente."""
    discente = models.ForeignKey(
        Discente,
        on_delete=models.CASCADE,
        related_name='reservas_livros'
    )
    livro = models.ForeignKey(
        Livro,
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    reservada_em = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ['-reservada_em']
        verbose_name = 'Reserva de Livro'
        verbose_name_plural = 'Reservas de Livros'

    def __str__(self):
        status = "ativa" if self.ativa else "cancelada"
        return f"{self.discente.nome} - {self.livro.titulo} ({status})"
