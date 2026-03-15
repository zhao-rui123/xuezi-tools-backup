from .smart_chart_recommender import SmartChartRecommender, recommend_chart, ChartType, DataPattern
from .document_with_charts import DocumentWithCharts, create_data_driven_report
from .template_manager import TemplateManager, TemplateBuilder, Template
from .advanced_charts import AdvancedChartGenerator, create_advanced_chart
from .html_reporter import InteractiveHTMLReporter, create_interactive_report
from .excel_generator import (
    ExcelTemplateGenerator,
    ExcelTemplateLibrary,
    create_excel_with_template,
    create_professional_excel
)
from .ppt_generator import (
    PPTTemplateGenerator,
    PPTTemplateLibrary,
    create_ppt_with_template,
    create_professional_ppt
)
from .office_advanced import (
    WordAdvancedFeatures,
    ExcelAdvancedFeatures,
    OfficeFormatConverter,
    BatchOfficeProcessor,
    protect_word_document,
    add_word_toc,
    excel_add_conditional_format
)
from .document_optimizer import (
    DocumentOptimizer,
    ContentSummarizer,
    ExcelOptimizer,
    PPTOptimizer,
    optimize_word,
    summarize_document,
    optimize_excel,
    optimize_ppt
)

__all__ = [
    'SmartChartRecommender',
    'recommend_chart',
    'ChartType',
    'DataPattern',
    'DocumentWithCharts',
    'create_data_driven_report',
    'TemplateManager',
    'TemplateBuilder',
    'Template',
    'AdvancedChartGenerator',
    'create_advanced_chart',
    'InteractiveHTMLReporter',
    'create_interactive_report',
    'ExcelTemplateGenerator',
    'ExcelTemplateLibrary',
    'create_excel_with_template',
    'create_professional_excel',
    'PPTTemplateGenerator',
    'PPTTemplateLibrary',
    'create_ppt_with_template',
    'create_professional_ppt',
    'WordAdvancedFeatures',
    'ExcelAdvancedFeatures',
    'OfficeFormatConverter',
    'BatchOfficeProcessor',
    'protect_word_document',
    'add_word_toc',
    'excel_add_conditional_format',
    'DocumentOptimizer',
    'ContentSummarizer',
    'ExcelOptimizer',
    'PPTOptimizer',
    'optimize_word',
    'summarize_document',
    'optimize_excel',
    'optimize_ppt'
]
