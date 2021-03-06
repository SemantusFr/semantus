// document.getElementById("presentation-card").classList.remove('bg-sucess');
    document.getElementById("presentation-card").classList.add('bg-link');
    document.getElementById("history-table-words-title").innerHTML = "Combinaisons"

    let initalized = 0;
    const storage = window.localStorage;
    const cold_color = '#ee0000';
    const hot_color = '#7ddc1f';
    const cls_newguess = "table-danger";
    const cls_guess = "table-info";
    const cls_hint = "hint";
    const puzzleNumber = {{puzzleNumber}};
    const fontSizeTextLargeScreen = '2.3rem';
    const fontSizeEmojiLargeScreen = '3.5rem';
    const fontSizeTextSmallScreen = '2.0rem';
    const fontSizeEmojiSmallScreen = '3.0rem';
    const circleSizeLargeScreen = '150px';
    const circleSizeSmallScreen = '125px';
    const maxLink = {{maxLink}};
    const maxScore = 3*maxLink;
    

    var fontSizeText = fontSizeTextLargeScreen;
    var fontSizeEmoji = fontSizeEmojiLargeScreen;
    var circleSize = circleSizeLargeScreen;
    var emoji = null;
    var today_word = null;
    var total_points = 0;
    var is_game_started = false;
    var already_won = false;
    var word_top = "";
    var word_bottom = "";
    var bestLinkScore = 0;
    

    $.getJSON(
            '/link/get_best_score',
            $.param({}, true),
            function(result){
                bestLinkScore = parseInt(result.best_score);
            });

    if (isMobileDevice()) {
        fontSizeText = fontSizeTextSmallScreen;
        fontSizeEmoji = fontSizeEmojiSmallScreen;
        circleSize = circleSizeSmallScreen;
    }

    document.getElementById("circle-container").style = `height: ${circleSize};`;

    function scrollToField()
    {
        // the next line is required to work around a bug in WebKit (Chrome / Safari)
        location.href = "#guess-1";
        location.href = "#guess-1";
    }

    function reload() {
        document.getElementById('popup-header-msg').innerHTML = "Nouveau jour !"
        message = "Temps écoulé, aujourd'hui est un nouveau jour !<br>";
        message += "Rechargement de la page en cours."
        document.getElementById('popup-msg').innerHTML = message;
        modal_message.show();
        setInterval(function() { window.location.reload(); }, 2000);
    }

    function checkDay() {
        const storagePuzzleNumber = storage.getItem("link_puzzleNumber");
        if (storagePuzzleNumber && storagePuzzleNumber != puzzleNumber) { reload(); }
    }

    const storagePuzzleNumber = storage.getItem("link_puzzleNumber");
    if (storagePuzzleNumber != puzzleNumber) {
        storage.removeItem("link_guesses");
        storage.setItem("link_puzzleNumber", puzzleNumber);
        guesses = [];
    } else {
        guesses = JSON.parse(storage.getItem("link_guesses"));
        if (guesses == null){
            guesses = [];
        } else {
            guesses.sort(function(x,y){return y[5]-x[5]});
            unlockHistory();
        }
    }
    
    // Get the modals to open popups from JS
    var modal_win = new bootstrap.Modal(document.getElementById('popup_win'), {
        keyboard: false
    })

    var modal_user_history = new bootstrap.Modal(document.getElementById('popup_user_history'), {
        keyboard: false
    })

    var modal_word_list = new bootstrap.Modal(document.getElementById('popup_list'), {
        keyboard: false
    })
    document.getElementById("list-words-column-name").innerHTML = "Combinaison(s)";

    var modal_message = new bootstrap.Modal(document.getElementById('popup_msg'), {
        keyboard: false
        })

    function sleep(milliseconds) {  
      return new Promise(resolve => setTimeout(resolve, milliseconds));  
    }  

    // Fill information for the user stat popup
    var userHistoryLink = document.getElementById("link-user-history");
    userHistoryLink.onclick = function() {
        data_stats = getStatsFromStorage();
        document.getElementById("user-history-table-content").innerHTML = '' 
        function add_row(name, value) {
            document.getElementById("user-history-table-content").innerHTML += 
            `<tr class="table-dark table-striped">
                <td class="text-white">${name}</td>
                <td class="text-white">${value}</td>
            </tr>`
        }        
        $.getJSON(
            '/get_date_from_puzzle_number',
            $.param({ number: data_stats.first_game}, true),
            function(result){
                add_row('Première partie :', result.date);
                add_row('Parties jouées :', data_stats.nb_games);
                add_row('Nombre moyen de mots trouvés :', (data_stats.nb_mean_guesses).toFixed(1));
                add_row('Nombre de moyen de 👍🏽 :', (data_stats.nb_mean_no_poop).toFixed(1));
                add_row('Nombre de moyen de 💩 :', (data_stats.nb_mean_poop).toFixed(1));
            });
        modal_user_history.show();
    }

    function getLinearProgressBar(id) {
        var bar = new ProgressBar.Line(`#progress-link-${id}`, {
        strokeWidth: 10,
        easing: 'easeInOut',
        duration: 800,
        color: '#FFEA82',
        trailColor: '#999',
        trailWidth: 10,
        svgStyle: {width: '100%', height: '100%'},
        from: {color: cold_color},
        to: {color: hot_color},
        step: (state, bar) => {
            bar.path.setAttribute('stroke', state.color);
        }
        });
        return bar
    }
    progress_link_1 = getLinearProgressBar(1)
    progress_link_2 = getLinearProgressBar(2)
    progress_link_3 = getLinearProgressBar(3)
    var field_guess_1 = document.getElementById("guess-1");
    var field_guess_2 = document.getElementById("guess-2");

    bar = new ProgressBar.Circle(progress, {
        strokeWidth: 10,
        trailWidth: 2,
        easing: 'easeInOut',
        duration: 1500,
        text: {
            autoStyleContainer: true
        },
        from: { color: cold_color, width: 10 },
        to: { color: hot_color, width: 10 },
        // Set default step function for all animate calls
        step: function(state, circle) {
            circle.path.setAttribute('stroke', state.color);
            circle.path.setAttribute('stroke-width', state.width);
            var value = circle.value();
            var score = Math.round(value*bestLinkScore);
            if (emoji) {
                circle.setText(emoji);
            } else {
                circle.setText(score);
            }
            circle.text.style.color = state.color;
        }
        });
        bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
        bar.text.style.fontSize = fontSizeText;

    // get THE word
    $.getJSON(
        'link/get_words',
        {},
        function(result){
            word_top = result.words[0];
            word_bottom = result.words[1];
            document.getElementById('word-top').value = word_top;
            document.getElementById('word-bottom').value = word_bottom;
        });
        
    field_guess_1.addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        document.getElementById("go").click();  
        }
    });

    field_guess_2.addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        document.getElementById("go").click();  
        }
    });

    var btn_submit = document.getElementById('go');
    btn_submit.addEventListener('click', function(){
        progress_link_1.animate(0.5);
        progress_link_2.animate(0.5);
        progress_link_3.animate(0.5);
        sleep(800).then(() => {
            let guess_1 = field_guess_1.value.trim().toLowerCase();
            let guess_2 = field_guess_2.value.trim().toLowerCase();
            if(guess_1 || guess_2) {
                $.getJSON(
                    '/link/get_score',
                    $.param({ guess_1: guess_1, guess_2: guess_2}, true),
                    function(result){
                        let score = result.score; 
                        let link_1 = result.link_1;
                        let link_2 = result.link_2;
                        let link_3 = result.link_3;
                        if (score >0) {
                            // document.getElementById("score_message").innerHTML = `${score} points`;
                            bar.animate(parseFloat(score)/parseFloat(bestLinkScore));
                            sleep(1600).then(() => {
                                    win(guess_1, guess_2, score);
                                }) 
                            
                        }
                        if (guess_1 == null || guess_1 == '') {
                            document.getElementById("value-link-1").innerHTML = "❌";
                            progress_link_1.animate(0.)
                        } else if (link_1 > 0) {
                            progress_link_1.animate(parseFloat(link_1)/maxLink)
                            document.getElementById("value-link-1").innerHTML = link_1;
                        } else if (link_1 == -1) {
                            document.getElementById("value-link-1").innerHTML = "🤔";
                            progress_link_1.animate(0.)
                        } else {
                            document.getElementById("value-link-1").innerHTML = "💩";
                            progress_link_1.animate(0.)
                        }
                        if (link_2 > 0) {
                            progress_link_2.animate(parseFloat(link_2)/maxLink)
                            document.getElementById("value-link-2").innerHTML = link_2;
                        } else {
                            if (link_1 > 0 && link_3 > 0) {
                                document.getElementById("value-link-2").innerHTML = "💩";
                            } else {
                                document.getElementById("value-link-2").innerHTML = "❌";
                            }
                            progress_link_2.animate(0.)
                        }
                        if (guess_2 == null || guess_2 == '') {
                            document.getElementById("value-link-3").innerHTML = "❌";
                            progress_link_3.animate(0.)
                        } else if(link_3 > 0) {
                            progress_link_3.animate(parseFloat(link_3)/maxLink)
                            document.getElementById("value-link-3").innerHTML = link_3;
                        } else if (link_3 == -1) {
                            document.getElementById("value-link-3").innerHTML = "🤔";
                            progress_link_3.animate(0.)
                        } else {
                            document.getElementById("value-link-3").innerHTML = "💩";
                            progress_link_3.animate(0.)
                        }
                        if (link_1 > -1 && link_2 >-1) {
                            addGuessToList(guess_1, guess_2, link_1, link_2, link_3, score);
                        }
                        
                        // empty the input field
                        // field_guess_1.value = "";
                        // field_guess_2.value = "";
                        if (isMobileDevice()) {
                            scrollToField();
                        }
                        focus();
                    }
                );
                
            } else {
                progress_link_1.animate(0.)
                progress_link_2.animate(0.)
                progress_link_3.animate(0.)
            }
        })
    });

    function addGuessToList(guess_1, guess_2, link_1, link_2, link_3, score) {
        isNew = true;
        guesses.forEach(function(entry) {
            let old_guess_1 = entry[0];
            let old_guess_2 = entry[1];
            if (old_guess_1 == guess_1 && old_guess_2 == guess_2) {
                isNew = false;  
            }
        });
        if (isNew) {
            console.log(score)
            if (score) {
                guesses.push([guess_1, guess_2, link_1, link_2, link_3, score]);
                guesses.sort(function(x,y){return y[5]-x[5]});
            }
        }          
    }

    var btn_share = document.getElementById('button-share')
        btn_share.addEventListener('click', function(){
            share();
        });

    function saveDataToCache(score) {
        let savedPuzzleNumber = storage.getItem("link_puzzleNumber");
        if (savedPuzzleNumber != puzzleNumber) {
            return;
        }
        storage.setItem("link_guesses", JSON.stringify(guesses));

        let data_day = JSON.parse(storage.getItem("link_day_"+puzzleNumber));
        if (data_day == null){
            data_day = {};
        }
        nb_guesses = guesses.length;
        if (data_day['score'] && data_day['score'] < score)
        {
            data_day['score'] = score;
        }
        data_day['nb_guesses'] = nb_guesses;
        storage.setItem("link_day_"+puzzleNumber, JSON.stringify(data_day));
    }

    function win(guess_1, guess_2, score)
    {
        unlockHistory();
        let message = "";
        // // check if you have already won
        saveDataToCache(score);
        document.getElementById('popup-win-title').innerHTML = '<h4 class="modal-title d-inline-block">Lien établi !</h4>';
        message += `<h5>Félicitation, tu as fait une chaine de mots de ${score} points !</h5>`;
        if (score == bestLinkScore)
        {
            message += "Il s'agit du meilleur score🏅, bravo !";
        } else {
            message += "C'est bien, mais tu peux faire encore mieux ! "; 
            message += `Le meilleur score possible est de ${bestLinkScore} points. <br>`;
            message += "Tu peux continuer à essayer d'augmenter ton score !";
        }
        document.getElementById("popup-win-msg").innerHTML = message;
        document.getElementById("div-block-hist").innerHTML = '';
        modal_win.show();
        // send data to server
        $.getJSON(
            '/link/win',
            $.param({guess_1: guess_1, guess_2: guess_2, score: total_points, user_id: get_user_id()}, true),
            function(result){});
    }

    function unlockHistory() {
        var btn_list = document.getElementById('full-list');
        
        btn_list.classList.remove('invisible');         
        btn_list.addEventListener('click', function(){
            modal_word_list.show();
            document.getElementById("modal-list-title").innerHTML = '<h5 class="modal-title">Combinaisons gagnantes trouvées</h5>';
            var table_content = '';
            
            guesses.forEach(function([guess_1, guess_2, link_1, link_2, link_3, score]) {
                table_content+=
                `
                                <tr>
                                    <td class="text-white">${guess_1+' + '+guess_2}</td>
                                    <td class="text-white">${score}</td>
                                </tr>
                `
                
                }
            )
            document.getElementById("modal-list-table-content").innerHTML = table_content;            
        });
    }

    /**
     * from https://andywalpole.me/blog/140739/using-javascript-create-guid-from-users-browser-information
     * @function _guid
     * @description Creates GUID for user based on several different browser variables
     * It will never be RFC4122 compliant but it is robust
     * @returns {Number}
     * @private
     */
    // I DO NOT STORE THIS, I HASH IT AND STORE THAT
    function get_user_id() {
        var nav = window.navigator;
        var screen = window.screen;
        var guid = nav.mimeTypes.length;
        guid += nav.userAgent.replace(/\D+/g, '');
        guid += nav.plugins.length;
        guid += screen.height || '';
        guid += screen.width || '';
        guid += screen.pixelDepth || '';

        return guid;
    };

    function get_text_winner(nb_winners) {
        if (nb_winners == 1)
        {
            return `${nb_winners}<sup>er·e</sup>`
        } else {
            return `${nb_winners}<sup>ème</sup>`
        }
    }
    focus();
    
    function isMobileDevice()
    {
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
            return true;
        } else {
            return false;
        }
    }   

    function focus()
    {
        document.getElementById("guess-1").focus();
    }

    function countPoops()
    {
        let nb_poop = 0;
        let nb_no_poop = 0;
        guesses.forEach(function (entry, index, arr) {
            let [word, number, score] = entry;
            if (score == 0)
            {
                nb_poop+=1;
            } else {
                nb_no_poop += 1;
            }
        });
        return [nb_poop, nb_no_poop];
    }

    
    async function share() {
        let user_best_score = 0;
        guesses.forEach(function(entry) {
            if (entry[5] > user_best_score)
            {
                user_best_score = entry[5];
            }
        });
        let message = "";
        if (user_best_score == bestLinkScore) {
            message = `J'ai trouvé la 🏅meilleure🏅 chaine de mots d'une valeur de ${user_best_score} 🏆`
        } else {
            message = `J'ai trouvé une chaine de mots d'une valeur de ${user_best_score} 🏆`
        }
        message += ` entre les deux mots du jours à #semantus 🔗Link🔗 (jour ${puzzleNumber}) !<br>`;
        message += "https://www.semantus.fr/link";

        try {
            await navigator.clipboard.writeText(message.replace(/<br>/g,'\n'));
            message += "<br><br>Copié dans le presse-papiers";
        } catch (err) {
            message += `<br><br>Erreur en copiant dans le presse-papiers<br>${err}`;
        }
        document.getElementById('popup-header-msg').innerHTML = 'Partage ton exploit !';
        document.getElementById('popup-msg').innerHTML = message;

        modal_win.hide();
        modal_message.show();
    }


    function beta() {   
        message = 'Bienvenue à Semantus <i class="italic text-link">Link</i> !';
        message += "<br><br>Ce jeu est en cours de développement, il est donc possible qu'il y reste des bugs.";
        message += "<br>N'hésitez pas à nous contacter si vous avez des questions ou des suggestions :";
        message += ' <a  href="https://twitter.com/intent/tweet?screen_name=semantusFr&ref_src=twsrc%5Etfw">@SemantuFr</a>';
        document.getElementById('popup-header-msg').innerHTML = "Jeu en version bêta !";
        document.getElementById('popup-msg').innerHTML = message;
        document.getElementById('btn-close-msg').focus();
        modal_message.show();
    }
    beta();