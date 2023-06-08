let DATA = 0;

        function loadData() {
            let xhr = new XMLHttpRequest();
            xhr.open(method="GET", url="/document{{doc.pk}}/getdata", async=true);
            
            xhr.onload = function() {
                let data = JSON.parse(xhr.response);

                if (data['is_liked']) {
                    likeBtn.innerHTML = `
                    {% include 'note_icons/caret_up_fill.html' %}
                    <span id="likeNum">${data['likes']}</span>
                    `;
                }
                else {
                    likeBtn.innerHTML = `
                    {% include 'note_icons/caret_up.html' %}
                    <span id="likeNum">${data['likes']}</span>
                    `;
                }

                if (data['is_disliked']) {
                    dislikeBtn.innerHTML = `
                    {% include 'note_icons/caret_down_fill.html' %}
                    <span id="dislikeNum">${-data['dislikes']}</span>
                    `;
                }
                else {
                    dislikeBtn.innerHTML = `
                    {% include 'note_icons/caret_down.html' %}
                    <span id="dislikeNum">${-data['dislikes']}</span>
                    `;
                }

                if (!data['bookmark']) {
                    bookmarkBtn.innerHTML = `{% include 'note_icons/bookmark.html' %}`
                }
                else {
                    bookmarkBtn.innerHTML = `{% include 'note_icons/bookmark_fill.html' %}`
                }

                commentBtn.innerHTML = `
                {% include 'note_icons/comment.html' %}
                <span id="dislikeNum">${data['comments']['count']}</span>
                `;

                if (data['comments']['count'] == 0) {
                    commentBlock.innerHTML = '';
                    let emptyTitle = document.createElement('h2');

                    emptyTitle.className = 'text-center';
                    emptyTitle.innerHTML = 'Пока здесь пусто!';

                    document.querySelector('#commentBlock').appendChild(emptyTitle); 
                }
                
                if (DATA != data['comments']['count']) {
                    commentBlock.innerHTML = '';
                    let comments = data['comments']['data'];

                    for (let i = 0; i < comments.length; ++i) {
                        let comment = document.createElement('div');
                        let commentBody = document.createElement('div');
                        let commentBottom = document.createElement('div');
                        let textMessage = document.createElement('p');
                        let deleteButton = document.createElement('div');
                        let author = document.createElement('span');
                        let date = document.createElement('span');

                        comment.id = `comment${i}`;
                        commentBottom.id = `commentBottom${i}`;
                        commentBody.id = `commentBody${i}`;

                        comment.className = 'm-1 p-1 border border-1 rounded text-emphasis-dark';
                        commentBottom.className = 'd-flex justify-content-between';
                        commentBody.className = 'd-flex justify-content-between';

                        if ('{{request.user}}' == comments[i]['author']) {
                            comment.className += ' bg-info-subtle';
                            
                            deleteButton.innerHTML = `<button 
                                                type="button" 
                                                class="btn-close" 
                                                aria-label="Close" 
                                                onclick="deleteComment(${comments[i]['pk']});setTimeout(loadData, 50)">
                                                </button>`;
                        }

                        textMessage.innerHTML = comments[i]['text'];
                        author.innerHTML = comments[i]['author'];
                        date.innerHTML = comments[i]['date'];
                        

                        document.querySelector(`#commentBlock`).appendChild(comment);
                        document.querySelector(`#${comment.id}`).appendChild(commentBody);
                        document.querySelector(`#${commentBody.id}`).appendChild(textMessage);
                        document.querySelector(`#${commentBody.id}`).appendChild(deleteButton);
                        document.querySelector(`#${comment.id}`).appendChild(commentBottom);
                        document.querySelector(`#${commentBottom.id}`).appendChild(date);
                        document.querySelector(`#${commentBottom.id}`).appendChild(author);
                    }
                }
                
                DATA = data['comments']['count'];

            }

            xhr.send();

        }

        function postLike() {
            let xhr = new XMLHttpRequest();
            xhr.open(method="POST", url="/documents/postlikedata", async=true);

            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader('X-CSRFToken', "{{ csrf_token }}");

            let response = {
                "doc": "{{doc.pk}}",
            }

            xhr.send(JSON.stringify(response));
        }

        function postDislike() {
            let xhr = new XMLHttpRequest();
            xhr.open(method="POST", url="/documents/postdislikedata", async=true);

            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader('X-CSRFToken', "{{ csrf_token }}");

            let response = {
                "doc": "{{doc.pk}}",
            }

            xhr.send(JSON.stringify(response));
        }

        function postComment() {
            let xhr = new XMLHttpRequest();
            xhr.open(method="POST", url="/documents/postcommentdata", async=true);

            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader('X-CSRFToken', "{{ csrf_token }}");

            let response = {
                'text': messageInput.value,
                "doc": "{{doc.pk}}",
            }
            messageInput.value = '';
            xhr.send(JSON.stringify(response));
        }

        function postBookmark() {
            let xhr = new XMLHttpRequest();
            xhr.open(method="POST", url="/documents/postbookmarkdata", async=true);

            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader('X-CSRFToken', "{{ csrf_token }}");

            let response = {
                "doc": "{{doc.pk}}",
            }

            xhr.send(JSON.stringify(response));
        }

        function deleteComment(pk) {
            let xhr = new XMLHttpRequest();
            xhr.open(method="POST", url="/documents/deletecomment", async=true);

            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.setRequestHeader('X-CSRFToken', "{{ csrf_token }}");

            let response = {
                "doc": "{{doc.pk}}",
                'comment': pk,
            }

            xhr.send(JSON.stringify(response));
        }

        function load() {
            loadData();
            setInterval(loadData, 10000);
        }
        