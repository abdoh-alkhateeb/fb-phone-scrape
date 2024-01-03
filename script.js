let response = await fetch("https://www.facebook.com/api/graphql/", {
    "headers": {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "dpr": "1",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"",
        "sec-ch-ua-full-version-list": "\"Not_A Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"120.0.6099.71\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-ch-ua-platform-version": "\"6.2.0\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "viewport-width": "752",
        "x-asbd-id": "129477",
        "x-fb-friendly-name": "GroupsCometFeedRegularStoriesPaginationQuery",
        "x-fb-lsd": "n7aq3Yl_YTlpNhCN4sMUrl"
    },
    "referrer": "https://www.facebook.com/groups/2869395429989324",
    "referrerPolicy": "strict-origin-when-cross-origin",
    "body": "av=61554736876057&__user=61554736876057&__a=1&__req=l&__hs=19724.HYP%3Acomet_pkg.2.1..2.1&dpr=1&__ccg=GOOD&__rev=1010625057&__s=er8aat%3Aufzvv1%3Adk3nny&__hsi=7319600149266647874&__dyn=7AzHK4HwkEng5K8G6EjBAo2nDwAxu13wFwhUKbgS3q2ibwNw9G2Saw8i2S1DwUx60GE3Qwb-q7oc81xoswIK1Rwwwqo465o-cwfG12wOx62G5Usw9m1YwBgK7o884y0Mo4G1hx-3m1mzXw8W58jwGzEaE5e7oqBwJK2W5olwUwgojUlDw-wUwxwjFovUaU3VBwFKq2-azqwqo4i223908O3216xi4UdUcojxK2B0oobo8oC1hxB0qo4e16wWwjHBU-4E&__csr=gz2kYdRPNbNXZRTviuzEGbtlFWtRPq44ObSaltZOiSWQRiR9WiQgjiVCjOWlkRHbqGiA8hQWjBFV-mXKq4pBJpfhfh-FHhpF8yqmp7LCKnyE-9BgWaHDK9zryogAxCmueyepByF8SWxfy9p8auimQqi4obXyEWeAyXwBGu9yEO5Ejx67UjzUqxa3612CwPx6ufyoK6okwzxedUaUrAxm1-wg9oPy8vwootxq2y1dwtod82wwzyE8uE6y1nw8u0QU32w3go1Po2Xw2bU1PTg065q02jO00PEolw9aawqo6204po2Kx60iadCg26DweS0FU1Jo1JPyE1fu03qmp01l-0tO0Ko08LUdo0fiE2Mw102075U0Jm2u1iDy8&__comet_req=15&fb_dtsg=NAcMjO66ZzymuzBfw_iFH4eSmtwWvDW97bzGBOtoXgBL2s8Za7Tt5Jg%3A43%3A1704137241&jazoest=25592&lsd=n7aq3Yl_YTlpNhCN4sMUrl&__aaid=0&__spin_r=1010625057&__spin_b=trunk&__spin_t=1704227214&qpl_active_flow_ids=431626709&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=GroupsCometFeedRegularStoriesPaginationQuery&variables=%7B%22UFI2CommentsProvider_commentsKey%22%3A%22CometGroupDiscussionRootSuccessQuery%22%2C%22count%22%3A3%2C%22cursor%22%3A%22Cg8TZXhpc3RpbmdfdW5pdF9jb3VudAICDwtyZWFsX2N1cnNvcg%2BrQVFIUmE3aHVSbEhfLVRBN0JEZjB6NUczeWNxRzdIWmZfdGhfWC01WnExSjRUUWdlWnduZUY3bk5NQnBIMHdXSldtZWFQcGtzWlZzNXBvdXBjaXJUNkc4TXR3OmV5SXdJam94TnpBME1qSTNNakUwTENJeElqb3pOVGcyTENJeUlqb3hOekEwTWpJM01EUXlMQ0l6SWpvd0xDSTBJam94TENJMUlqb3lmUT09DxNoZWFkZXJfZ2xvYmFsX2NvdW50AgEPEm1haW5fZmVlZF9wb3NpdGlvbgICDw1mZWVkX29yZGVyaW5nDxtyYW5rZWRfaW50ZXJlc3RfY29tbXVuaXRpZXMPE2lzX2V2ZXJncmVlbl9jdXJzb3IRAA8iaXNfb2ZmbGluZV9hZ2dyZWdhdGVkX3Bvc3RzX2N1cnNvchEADxJncm91cF9mZWVkX3ZlcnNpb24PAlYyDxBkZW1vdGVkX3Bvc3RfaWRzCgEB%22%2C%22displayCommentsContextEnableComment%22%3Anull%2C%22displayCommentsContextIsAdPreview%22%3Anull%2C%22displayCommentsContextIsAggregatedShare%22%3Anull%2C%22displayCommentsContextIsStorySet%22%3Anull%2C%22displayCommentsFeedbackContext%22%3Anull%2C%22feedLocation%22%3A%22GROUP%22%2C%22feedType%22%3A%22DISCUSSION%22%2C%22feedbackSource%22%3A0%2C%22focusCommentID%22%3Anull%2C%22privacySelectorRenderLocation%22%3A%22COMET_STREAM%22%2C%22renderLocation%22%3A%22group%22%2C%22scale%22%3A1%2C%22sortingSetting%22%3Anull%2C%22stream_initial_count%22%3A1%2C%22useDefaultActor%22%3Afalse%2C%22id%22%3A%222869395429989324%22%2C%22__relay_internal__pv__IsWorkUserrelayprovider%22%3Afalse%2C%22__relay_internal__pv__IsMergQAPollsrelayprovider%22%3Afalse%2C%22__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider%22%3Afalse%2C%22__relay_internal__pv__CometUFIIsRTAEnabledrelayprovider%22%3Afalse%2C%22__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider%22%3Afalse%2C%22__relay_internal__pv__StoriesRingrelayprovider%22%3Afalse%7D&server_timestamps=true&doc_id=7134241823307235",
    "method": "POST",
    "mode": "cors",
    "credentials": "include"
});

let data = await response.text();

return data;
