# php-backend-test-tool
A basic script for sanity-checking a php-backend with gson-responses.

Runs through a php folder and its subfolders and sends a GET requests to all directories that contains an index.php file. The requests is joined with a provided root url, e.g. localhost.

The script expects the GET-requests to return gson-complient responses with a 200.

# Use
./validate.py --help
