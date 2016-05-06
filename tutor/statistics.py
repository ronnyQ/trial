from main.models import Student_response, Question_option

class Statistics():
    def get_question_totals(self, question_id, session_run_id):
        options = Question_option.objects.filter(question=question_id)
        responses = Student_response.objects.filter(option__question=question_id, session_run=session_run_id)

        # Build up a data structure containing each option and a count of how many times
        # that option was picked
        option_totals = {}
        for option in options:
            totals_entry = {
                'option_body': option.body,
                'option_correct': option.correct,
                'count': 0
            }

            option_totals[option.id] = totals_entry

        for response in responses:
            # Increment the count against the option that the student selected
            option_totals[response.option.id]['count'] += 1

        return option_totals