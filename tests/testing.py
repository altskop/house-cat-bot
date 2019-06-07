from responses import response_builder


class UnitTester():

    test_num = 0
    tests_passed = 0

    def __init__(self):
        self.resp = response_builder.ResponseBuilder(None)


    def unit_test_fits_template(self, key, string, expected_result):
        self.test_num += 1
        test_type = "msg_fits_template(\""+key+"\", \""+string+"\")"

        result = self.resp.msg_fits_template(key, string)
        if expected_result is not result:
            test_result = "[FAILED] for test #" + str(self.test_num) + " " + test_type + \
                          ". Expected: "+str(expected_result)+"; Received: " + str(result)
        else:
            test_result = "[PASSED] for test #" + str(self.test_num) + " " + test_type
            self.tests_passed += 1
        print(test_result)

    def unit_test_truncate_mentions(self, string, expected_result):
        self.test_num += 1
        test_type = "truncate_mentions(\"" + string + "\")"

        result = self.resp.truncate_mentions(string)
        if expected_result != result:
            test_result = "[FAILED] for test #" + str(self.test_num) + " " + test_type + \
                          ". Expected: " + str(expected_result) + "; Received: " + str(result)
        else:
            test_result = "[PASSED] for test #" + str(self.test_num) + " " + test_type
            self.tests_passed += 1
        print(test_result)

    def print_results(self):
        tests_failed = self.test_num - self.tests_passed
        print("---------------------------------------------\n" +
              "TOTAL TESTS RAN: "+str(self.test_num) + "\n" +
              "PASSED: "+str(self.tests_passed)+"  |  FAILED: "+str(tests_failed)
              )


test = UnitTester()

test.unit_test_fits_template("INSULT", "u r good", False)
test.unit_test_fits_template("INSULT", "u r dumb", True)
test.unit_test_fits_template("INSULT", "u r a bitch", True)
test.unit_test_fits_template("INSULT", "u r a lil bitch", True)
test.unit_test_fits_template("INSULT", "u r a little bitch", True)
test.unit_test_fits_template("INSULT", "your a bitch", True)
test.unit_test_fits_template("INSULT", "your a goof", False)
test.unit_test_fits_template("INSULT", "you are a bitch", True)
test.unit_test_fits_template("INSULT", "you r dumb", True)
test.unit_test_fits_template("INSULT", "youre awesome", False)
test.unit_test_fits_template("INSULT", "you suck", True)
test.unit_test_fits_template("INSULT", "u dumb", True)

test.unit_test_truncate_mentions("<@303023298743238656> you're dumb", "you're dumb")
test.unit_test_truncate_mentions("you're dumb <@303023298743238656>", "you're dumb")
test.unit_test_truncate_mentions("<@303023298743238656> <@303023298743238656> you're dumb", "you're dumb")
test.unit_test_truncate_mentions("you're dumb <@303023298743238656> <@303023298743238656>", "you're dumb")
test.unit_test_truncate_mentions("<@303023298743238656>", "")

test.print_results()