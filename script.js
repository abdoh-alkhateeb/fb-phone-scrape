const getData = async () => {
    try {
        const response = await fetch("https://www.facebook.com/api/graphql/", {
            "credentials": "include",
            "headers": {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-FB-Friendly-Name": "GroupsCometFeedRegularStoriesPaginationQuery",
                "X-FB-LSD": "Xf3lGpglNYL8P_CcmscGcB",
                "X-ASBD-ID": "129477",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin"
            },
            "referrer": "https://www.facebook.com/groups/2869395429989324",
            "body": "av=61554736876057&__user=61554736876057&__a=1&__req=o&__hs=19722.HYP%3Acomet_pkg.2.1..2.1&dpr=1&__ccg=EXCELLENT&__rev=1010617027&__s=3t1sus%3Alzov9z%3A4pe626&__hsi=7318883896591602362&__dyn=7AzHK4HwkEng5K8G6EjBAo2nDwAxu13wFwhUngS3q2ibwNw9G2Saw8i2S1DwUx60GE3Qwb-q7oc81xoswIK1Rwwwqo465o-cwfG12wOx62G5Usw9m1YwBgK7o884y0Mo4G1hx-3m1mzXw8W58jwGzEaE5e7oqBwJK2W5olwUwgojUlDw-wUwxwjFovUaU3VBwFKq2-azqwqo4i223908O3216xi4UdUcojxK2B0oobo8oC1hxB0qo4e16wWwjHBU-4E&__csr=gZ3It4p1AQDAbkBhll_WWAFHAnOPF95FmGkmOuOlO8z_eFqLYHl8Th4TGCykiBiGGt5HBWz5HGGAqmDyGKmF9EoLGbHVWGt7Czk4ECh7D-q9KqimGgymcyGCy49qCiCzUS5Ubu7-iiFby8lyoSi9LG4988EggrGfwAxm7ovxei3m9z43a2eq2Wi3210z9o8oXwMG2fzE5u1iwzxu2Tx62W3G7ojw-w9i2q0WEcE89UaU56786a0N87W0m61Xw1ri0dlix100jZU0119Ulw49gO3e04-o9U6O0lyEHw4Rwbu0Z87m0rIHy40hLw0SAo0o2w4Tw5vw0xKw0YVw9G0dDw0wLw2f626&__comet_req=15&fb_dtsg=NAcN0FTv8a25jWwI4ZSAVIPdQQgPKNkSaNhp4oZTBcGGCXuplg_ed_Q%3A24%3A1704060062&jazoest=25424&lsd=Xf3lGpglNYL8P_CcmscGcB&__aaid=0&__spin_r=1010617027&__spin_b=trunk&__spin_t=1704060448&qpl_active_flow_ids=431626709&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=GroupsCometFeedRegularStoriesPaginationQuery&variables=%7B%22UFI2CommentsProvider_commentsKey%22%3A%22CometGroupDiscussionRootSuccessQuery%22%2C%22count%22%3A3%2C%22cursor%22%3A%22Cg8TZXhpc3RpbmdfdW5pdF9jb3VudAICDwtyZWFsX2N1cnNvcg%2BrQVFIUjN3dWU2N2Q5RGYyWGZIRkphYzhCam9GMHR0Wm0yU3UzWVI0dTRDeDdKN2hyVEJsTS0tRTU4dkFjWGlZQlhtS2NublVtWHVfVzBJdi1lZUl6X2Vnb2VROmV5SXdJam94TnpBME1EWXdORFE0TENJeElqb3pOVGcyTENJeUlqb3hOekEwTURZd01qSXhMQ0l6SWpvd0xDSTBJam94TENJMUlqb3lmUT09DxNoZWFkZXJfZ2xvYmFsX2NvdW50AgEPEm1haW5fZmVlZF9wb3NpdGlvbgICDw1mZWVkX29yZGVyaW5nDxtyYW5rZWRfaW50ZXJlc3RfY29tbXVuaXRpZXMPE2lzX2V2ZXJncmVlbl9jdXJzb3IRAA8iaXNfb2ZmbGluZV9hZ2dyZWdhdGVkX3Bvc3RzX2N1cnNvchEADxJncm91cF9mZWVkX3ZlcnNpb24PAlYyDxBkZW1vdGVkX3Bvc3RfaWRzCgEB%22%2C%22displayCommentsContextEnableComment%22%3Anull%2C%22displayCommentsContextIsAdPreview%22%3Anull%2C%22displayCommentsContextIsAggregatedShare%22%3Anull%2C%22displayCommentsContextIsStorySet%22%3Anull%2C%22displayCommentsFeedbackContext%22%3Anull%2C%22feedLocation%22%3A%22GROUP%22%2C%22feedType%22%3A%22DISCUSSION%22%2C%22feedbackSource%22%3A0%2C%22focusCommentID%22%3Anull%2C%22privacySelectorRenderLocation%22%3A%22COMET_STREAM%22%2C%22renderLocation%22%3A%22group%22%2C%22scale%22%3A1%2C%22sortingSetting%22%3Anull%2C%22stream_initial_count%22%3A1%2C%22useDefaultActor%22%3Afalse%2C%22id%22%3A%222869395429989324%22%2C%22__relay_internal__pv__IsWorkUserrelayprovider%22%3Afalse%2C%22__relay_internal__pv__IsMergQAPollsrelayprovider%22%3Afalse%2C%22__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider%22%3Afalse%2C%22__relay_internal__pv__CometUFIIsRTAEnabledrelayprovider%22%3Afalse%2C%22__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider%22%3Afalse%2C%22__relay_internal__pv__StoriesRingrelayprovider%22%3Afalse%7D&server_timestamps=true&doc_id=7134241823307235",
            "method": "POST",
            "mode": "cors"
        });

        const { data } = await response.json();
        console.log(data);
    } catch (e) {
        console.log("Error: ", e);
    }
};

getData();
