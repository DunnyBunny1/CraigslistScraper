"""Google Cloud Function entry point for bike alert system"""
import functions_framework
import logging
from pipeline import run_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


@functions_framework.http
def check_new_bikes(request):
    """
    HTTP Cloud Function entry point.

    Google calls this function when triggered.
    The 'request' parameter is required by Cloud Functions but we don't use it.

    :param request: Flask request object (provided by Cloud Functions)
    :return: Tuple of (message, http_status_code)
    """
    log.info("🚀 Cloud Function triggered - starting bike alert check")

    try:
        run_pipeline()
        log.info("Bike alert check completed successfully")
        return "Bike check completed successfully", 200

    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)
        return f"Error: {str(e)}", 500
