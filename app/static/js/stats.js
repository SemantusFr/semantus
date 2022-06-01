export function getClassicStatsFromStorage(puzzleNumber)
{
    let nb_guesses_tot = 0;
    let nb_hints_tot = 0;
    let nb_guesses_and_hints_tot = 0;
    let nb_points_tot = 0;
    let rank = 0;
    let nb_points = null;
    let first_game = null;
    
    let nb_guesses_win = 0;
    let nb_hints_win = 0;
    let nb_win = 0;
    let nb_no_win = 0;
    let previous_day = null;
    let win_streak = 0;
    let nb_games = 0;

    for (let day = 0; day < puzzleNumber+1; day++) { 
        let entry = storage.getItem("day_"+day);
        try {
            let data_day = JSON.parse(entry);
            if (entry != null) {
                nb_games += 1;
                nb_guesses_tot += parseInt(data_day.nb_guesses);
                nb_hints_tot += parseInt(data_day.nb_hints);
                nb_guesses_and_hints_tot += parseInt(data_day.nb_guesses_and_hints);
                rank = data_day.rank;
                nb_points = data_day.nb_points;
                // find the first day played
                if (first_game == null || day < first_game) {
                    first_game = day;
                }
                let score = data_day.nb_points;
                // find number of wins and no wins
                if (score != null) {
                    nb_win += 1;
                    nb_guesses_win += parseInt(data_day.nb_guesses);
                    nb_hints_win += parseInt(data_day.nb_hints);
                    nb_points_tot += nb_points;
                } else {
                    nb_no_win += 1;
                }
                // compute win streak
                let win = nb_points != null;
                if (win) {
                    if (previous_day != null && (day - previous_day == 1)) {
                        win_streak += 1;
                    } else {
                        win_streak = 1;
                    }
                } else {
                    win_streak = 0;
                }
                previous_day = day;
            }
        } catch (e) {
        console.log('Error parsing day '+day+': '+e);
        return null;
        }
    }
    let nb_mean_guesses_win = 0;
    let nb_mean_hints_win = 0;
    let nb_mean_points = 0;
    
    if (nb_win > 0) {
        nb_mean_guesses_win = parseFloat(nb_guesses_win)/nb_win;
        nb_mean_hints_win = parseFloat(nb_hints_win)/nb_win;
        nb_mean_points = parseFloat(nb_points_tot)/nb_win;
    }
    let stats = {
        "first_game": first_game,
        "win_streak": win_streak,
        "nb_mean_guesses_win": nb_mean_guesses_win,
        "nb_mean_hints_win": nb_mean_hints_win,
        "nb_guesses_and_hints_tot": nb_guesses_tot+nb_hints_tot,
        "nb_guesses_tot": nb_guesses_tot,
        "nb_hints_tot": nb_hints_tot,
        "nb_games": nb_games,
        "nb_win": nb_win,
        "nb_no_win": nb_no_win,
        "nb_mean_points": nb_mean_points,
    }
    return stats;
};

export function getFlashStatsFromStorage(puzzleNumber)
{
    let nb_guesses_tot = 0;
    let nb_points_tot = 0;
    let first_game = null;
    let nb_no_poop_tot = 0;
    let nb_poop_tot = 0;
    let nb_games = 0;

    for (let day = 0; day < puzzleNumber+1; day++) { 
        let entry = storage.getItem("flash_day_"+day);
        try {
            let data_day = JSON.parse(entry);
            if (entry != null) {
                nb_games += 1;
                if (data_day.nb_guesses) {nb_guesses_tot += parseInt(data_day.nb_guesses);}
                if (data_day.score) {nb_points_tot += data_day.score;}
                if (data_day.nb_no_poop) {nb_no_poop_tot += data_day.nb_no_poop;}
                if (data_day.nb_poop) {nb_poop_tot += data_day.nb_poop;}
                // find the first day played
                if (first_game == null || day < first_game) {
                    first_game = day;
                }
            }
        } catch (e) {
            console.log('Error parsing day '+day+': '+e);
        }
    }
    let nb_mean_guesses = 0;
    let nb_mean_poop = 0;
    let nb_mean_no_poop = 0;
    let nb_mean_points = 0;
    
    if (nb_games) {
        nb_mean_guesses = parseFloat(nb_guesses_tot)/nb_games;
        nb_mean_poop = parseFloat(nb_poop_tot)/nb_games;
        nb_mean_no_poop = parseFloat(nb_no_poop_tot)/nb_games;
        nb_mean_points = parseFloat(nb_points_tot)/nb_games;
    }
    let stats = {
        "first_game": first_game,
        "nb_mean_guesses": nb_mean_guesses,
        "nb_mean_poop": nb_mean_poop,
        "nb_mean_no_poop": nb_mean_no_poop,
        "nb_guesses_tot": nb_guesses_tot,
        "nb_games": nb_games,
        "nb_mean_points": nb_mean_points,
    }
    return stats;
};

export function getLinkStatsFromStorage(puzzleNumber)
{
    let nb_guesses_tot = 0;
    let nb_points_tot = 0;
    let first_game = null;
    let nb_games = 0;

    for (let day = 0; day < puzzleNumber+1; day++) { 
        let entry = storage.getItem("link_day_"+day);
        try {
            let data_day = JSON.parse(entry);
            if (entry != null) {
                nb_games += 1;
                if (data_day.nb_guesses) {nb_guesses_tot += parseInt(data_day.nb_guesses);}
                if (data_day.score) {nb_points_tot += data_day.score;}
                // find the first day played
                if (first_game == null || day < first_game) {
                    first_game = day;
                }
            }
        } catch (e) {
            console.log('Error parsing day '+day+': '+e);
        }
    }
    let nb_mean_guesses = 0;
    let nb_mean_points = 0;
    
    if (nb_games) {
        nb_mean_guesses = parseFloat(nb_guesses_tot)/nb_games;
        nb_mean_points = parseFloat(nb_points_tot)/nb_games;
    }
    let stats = {
        "first_game": first_game,
        "nb_mean_guesses": nb_mean_guesses,
        "nb_guesses_tot": nb_guesses_tot,
        "nb_games": nb_games,
        "nb_mean_points": nb_mean_points,
    }
    return stats;
};