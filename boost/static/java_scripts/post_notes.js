function postLike() {
    let xhr = new XMLHTTPRequest(method="POST", url="/document{{doc.pk}}/postlikedata", async=true);

    let response = {
        "doc": "{{doc.pk}}",
        "author": "{{user}}",
    }

    xhr.send(JSON.stringify(response));
}