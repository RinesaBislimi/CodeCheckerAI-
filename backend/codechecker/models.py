from django.db import models

class CodeSnippet(models.Model):
    code = models.TextField()
    result = models.TextField()

class AnalysisResult(models.Model):
    snippet = models.ForeignKey(CodeSnippet, on_delete=models.CASCADE, related_name='analysis_results')
    analysis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for CodeSnippet {self.snippet.id}"
