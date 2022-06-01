// document.getElementById("presentation-card").classList.remove('bg-sucess');
function clap(puzzleNumber) {
    document.getElementById("presentation-card").classList.add('bg-link');
    document.getElementById("history-table-words-title").innerHTML = "Combinaisons"

    let initalized = 0;
    const storage = window.localStorage;
    const cold_color = '#ee0000';
    const hot_color = '#7ddc1f';
    const cls_newguess = "table-danger";
    const cls_guess = "table-info";
    const cls_hint = "hint";
    const fontSizeTextLargeScreen = '2.3rem';
    const fontSizeEmojiLargeScreen = '3.5rem';
    const fontSizeTextSmallScreen = '2.0rem';
    const fontSizeEmojiSmallScreen = '3.0rem';
    const circleSizeLargeScreen = '150px';
    const circleSizeSmallScreen = '125px';

    

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

    // $.getJSON(
    //         '/link/get_best_score',
    //         $.param({}, true),
    //         function(result){
    //             bestLinkScore = parseInt(result.best_score);
    //         });

    const storagePuzzleNumber = storage.getItem("clap_puzzleNumber");
    if (storagePuzzleNumber != puzzleNumber) {
        // storage.removeItem("link_guesses");
        // storage.setItem("link_puzzleNumber", puzzleNumber);
        // guesses = [];
    } else {
        // guesses = JSON.parse(storage.getItem("link_guesses"));
        // if (guesses == null){
        //     guesses = [];
        // } else {
        //     guesses.sort(function(x,y){return y[5]-x[5]});
        //     unlockHistory();
        // }
    }

    var btn_submit = document.getElementById('go');
    btn_submit.addEventListener('click', function(){
        
    });
}
    

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