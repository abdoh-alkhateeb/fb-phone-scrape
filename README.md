# Facebook Scraper

## Overview
This Facebook Scraper is designed to extract all posts and comments from a Facebook group by leveraging GraphQL calls made by the web UI. It replays these calls with the appropriate parameters to retrieve data effectively. As of January 11th, 2024, the scraper is compatible with Facebook's GraphQL API.

## GraphQL Queries Used
The application utilizes the following GraphQL queries:
- GroupsCometFeedRegularStoriesPaginationQuery
- CommentListComponentsRootQuery
- CommentsListComponentsPaginationQuery
- Depth1CommentsListPaginationQuery
- Depth2CommentsListPaginationQuery

## Getting Started
1. Install the required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```
   
2. To initiate the application, run the following command:
   ```bash
   python main.py
   ```

### Configuration
Ensure that your `config.json` file contains the necessary fields:

```json
{
   "FB_EMAIL": "your_email@example.com",
   "FB_PASSWORD": "your_password",
   "FB_GROUP_ID": "your_facebook_group_id",
   "CHROME_BINARY": "path/to/chromium",
   "DUMP_DIRECTORY": "path/to/dump_directory"
}
```

## Important Note
This scraper relies on the Chromium webdriver. Make sure to provide valid credentials and paths in the configuration file for successful execution.

Happy scraping!
