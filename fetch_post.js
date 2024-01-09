const response = await fetch("https://www.facebook.com/api/graphql/", {
    "headers": {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "dpr": "1",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"",
        "sec-ch-ua-full-version-list": "\"Not_A Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"120.0.6099.199\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-ch-ua-platform-version": "\"6.2.0\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "viewport-width": "1080",
        "x-asbd-id": "129477",
        "x-fb-friendly-name": "GroupsCometFeedRegularStoriesPaginationQuery"
    },
    "referrer": "",
    "referrerPolicy": "strict-origin-when-cross-origin",
    "body": "",
    "method": "POST",
    "mode": "cors",
    "credentials": "include"
});

const data = await response.text();

return data;
