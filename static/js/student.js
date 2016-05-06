function RunningSesson(sessionCode) {
    this.sessionCode = sessionCode;

    this.checkForQuestions = function() {
        $.get('/student/check_question_availability/', {
            'session_code': this.sessionCode
        }, function(response) {
            if (response.question_available) {
                setTimeout(function() {
                    showQuestion(response);
                }, response.time_to_start);
            } else {
                // If there were no questions, check again in 2 seconds
                setTimeout(runningSession.checkForQuestions, 2000);
            }
        });
    };

    showQuestion = function(question) {
        $('#question-title').text(question.question_body);
        var question_option_template = $('#template-question-option').text();
        for (var i = question.question_options.length - 1; i >= 0; i--) {
            option = question.question_options[i];
            option_html = question_option_template;
            option_html = option_html.replace(/\[\# option_id \#\]/g, option.id);
            option_html = option_html.replace(/\[\# option_body \#\]/g, option.body);
            $('#question-option-container').append(option_html);
        };
        $('#wait-container').fadeOut(function() {
            $('#question-container').fadeIn();
        });
    };
}

var runningSession = new RunningSesson(sessionCode);