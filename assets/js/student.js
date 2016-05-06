var allowedToRespond = true;
function RunningSesson(sessionCode) {
    this.sessionCode = sessionCode;

    this.checkForQuestions = function(sessionCode, responderUUID) {
        allowedToRespond = true;
        $.get('/student/check_question_availability/', {
            'session_code': sessionCode,
            'responder_uuid': responderUUID
        }, function(response) {
            if (response.question_available) {
                setTimeout(function() {
                    showQuestion(response);
                }, response.time_to_start);
            } else {
                // If there were no questions, check again in 2 seconds
                setTimeout(function() {runningSession.checkForQuestions(sessionCode, responderUUID)}, 2000);
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
            startQuestionTimer(question.run_time);
        });
    };

    startQuestionTimer = function(runTime) {
        var progressBarDelay = (runTime * 1000) / 100;
        var progressBarWidth = 0;
        var progressBarInterval = setInterval(function() {
            progressBarWidth++;
            $('#time-remaining-progress .progress-bar').width(progressBarWidth + '%');

            // Stop the progress bar once full
            if (progressBarWidth == 100) {
                clearInterval(progressBarInterval);
            }
        }, progressBarDelay);

        // Count down in seconds on the display
        var secondsRemaining = runTime;
        $('#seconds-remaining').text(secondsRemaining);
        var countdownInterval = setInterval(function() {
            secondsRemaining--;
            $('#seconds-remaining').text(secondsRemaining);

            if (secondsRemaining == 0) {
                clearInterval(countdownInterval);
                questionComplete();
            }
        }, 1000);
    };

    transmitResponse = function(optionId) {
        if (allowedToRespond) {
            $.post('/student/log_response/', {
                'optionId': optionId,
                'sessionCode': this.sessionCode
            });
        }
        allowedToRespond = false;
    };


    resetQuestionArea = function() {
        // Remove all question buttons
        $('.question-option-button').remove();
        // Reset the progress bar to zero
        $('#time-remaining-progress .progress-bar').css('width', '0px');
    };

    uiToWaiting = function() {
        $('#question-container:visible, #response-transmitted-container:visible').fadeOut(function() {
            $('#wait-container').fadeIn();
        });
    };

    uiToResponseTransmitted = function() {
        $('#question-container:visible').fadeOut(function() {
            $('#response-transmitted-container').fadeIn();
        });
    };

    // createUUID function taken from - http://stackoverflow.com/a/873856
    createUUID = function() {
        // http://www.ietf.org/rfc/rfc4122.txt
        var s = [];
        var hexDigits = "0123456789abcdef";
        for (var i = 0; i < 36; i++) {
            s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
        }
        s[14] = "4";  // bits 12-15 of the time_hi_and_version field to 0010
        s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1);  // bits 6-7 of the clock_seq_hi_and_reserved to 01
        s[8] = s[13] = s[18] = s[23] = "-";

        var uuid = s.join("");
        return uuid;
    }
    this.responderUUID = createUUID(); // This is used to identify the responder

    questionComplete = function() {
        resetQuestionArea();
        uiToWaiting();
        runningSession.checkForQuestions(runningSession.sessionCode, runningSession.responderUUID);
    };

    // Binding for question options being clicked
    $(document).on('click', '.question-option-button', function() {
        uiToResponseTransmitted();

        var option_id = $(this).attr('data-option-id');
        transmitResponse(option_id);
    });

    this.checkForQuestions(this.sessionCode, this.responderUUID);
}

var runningSession = new RunningSesson(sessionCode);