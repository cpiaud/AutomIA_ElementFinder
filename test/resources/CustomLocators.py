from robot.libraries.BuiltIn import BuiltIn
from SeleniumLibrary.base import LibraryComponent, keyword


class CustomLocators(LibraryComponent):

    def __init__(self, ctx):
        super(CustomLocators, self).__init__(ctx)

    # def by_testid(locator):
    #     seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
    #     element = seleniumlib._element_find("xpath://input[@name='%s']" % locator, True, True)
    #     return element

    @staticmethod
    def by_testid(locator):
        seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        xpath_expression = "//input[@name='%s']" % locator
        print("Generated XPath:", xpath_expression)
        element = seleniumlib._element_find(xpath_expression, True, True)
        return element

    @keyword
    def by_name(locator):
        seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
        xpath_expression = "//input[@name='%s']" % locator
        print("Generated XPath:", xpath_expression)
        element = seleniumlib._element_find(xpath_expression, True, True)
        return element
