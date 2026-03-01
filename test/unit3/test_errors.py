""" Unit test for error handling"""
import unittest

class TryExceptFinallyTest(unittest.TestCase):
    def test_try(self):
        a,b,c,d,e,f,g = False, False, False, False, False, False, False
        try:
            a = True
            try:
                b = True
                i = int('badint');
                c = True
            except:
                d = True
            e = True
            i = float('otherbadint')
            f = True
        except:
            g = True
        self.assertTrue(a)
        self.assertTrue(b)
        self.assertFalse(c)
        self.assertTrue(d)
        self.assertTrue(e)
        self.assertFalse(f)
        self.assertTrue(g)

    def test_except(self):
        def test(i):
            f = 3
            try:
                return f == 5
            except ValueError:
                return True
        self.assertFalse(test(12))

    def test_errors(self):
        error1, error2, error3, error4, error5, error6, error7 = None, None, None, None, None, None, None
        try:
            assert 1 > 10
        except AssertionError:
            error1 = "caught error"
        except:
            error1 = "missed error"
        self.assertEqual(error1, "caught error")
        try:
            error2 = None.notAnAttribute
        except AttributeError:
            error2 = "Caught AttributeError"
        except:
            error2 = "Did not catch AttributeError"
        self.assertEqual(error2, "Caught AttributeError")
        try:
            import notAModule
        except ImportError:
            error3 = "Caught ImportError"
        except:
            error3 = "Did not catch ImportError"
        self.assertEqual(error3, "Caught ImportError")
        try:
            error4 = [0,1,2,3,4][5]
        except IndexError:
            error4 = "Caught IndexError"
        except:
            error4 = "Did not catch IndexError"
        self.assertEqual(error4, "Caught IndexError")
        try:
            print({1:2, 3:4}[5])
        except KeyError:
            error5 = "Caught KeyError"
        except:
            error5 = "Did not catch KeyError"
        self.assertEqual(error5, "Caught KeyError")
        try:
            error6 = x
        except NameError:
            error6 = "Caught NameError"
        except:
            error6 = "Did not catch NameError"
        self.assertEqual(error6, "Caught NameError")
        try:
            print(0.0000000000000000000000000000000000000000000000000000000000000001**-30)
        except OverflowError:
            error7 = "Caught OverflowError"
        except:
            error7 = "Did not catch OverflowError"
        self.assertEqual(error7, "Caught OverflowError")


    def test_exception(self):
        class C:
            def __init__(self):
              try:
                raise Exception("Oops")
              except:
                self.x = "Caught"
        c = C()
        self.assertEqual(c.x, "Caught")

    def test_bad_exception(self):
        # Skulpt Bug
        class InvalidException:
            # does not inherit from BaseException
            pass

        with self.assertRaises(TypeError) as c:
            raise InvalidException
        self.assertIn("BaseException", c.exception.args[0])
        
        with self.assertRaises(TypeError):
            raise InvalidException()

        with self.assertRaises(TypeError):
            raise 1


class AssertTests(unittest.TestCase):
    def test_assert_simple_pass(self):
        assert True
        assert 1 == 1
        assert 1 != 2
        assert 1 < 2
        assert 2 > 1
        assert 1 <= 1
        assert 1 >= 1

    def test_assert_simple_fail(self):
        with self.assertRaises(AssertionError):
            assert False

    def test_assert_comparison_fail(self):
        with self.assertRaises(AssertionError):
            assert 1 == 2
        with self.assertRaises(AssertionError):
            assert 1 > 2
        with self.assertRaises(AssertionError):
            assert 2 < 1
        with self.assertRaises(AssertionError):
            assert 1 != 1
        with self.assertRaises(AssertionError):
            assert 2 <= 1
        with self.assertRaises(AssertionError):
            assert 1 >= 2

    def test_assert_identity_fail(self):
        a = [1]
        b = [1]
        with self.assertRaises(AssertionError):
            assert a is b
        a = object()
        with self.assertRaises(AssertionError):
            assert a is not a

    def test_assert_with_message(self):
        with self.assertRaises(AssertionError) as ctx:
            assert 1 == 2, "custom message"
        self.assertIn("custom message", str(ctx.exception))

    def test_assert_with_message_pass(self):
        assert 1 == 1, "should not appear"
        assert True, "should not appear"

    def test_assert_chained_comparison(self):
        assert 1 < 2 < 3
        with self.assertRaises(AssertionError):
            assert 1 < 2 < 1

    def test_assert_non_compare(self):
        assert [1, 2, 3]
        assert "non-empty"
        assert 42
        with self.assertRaises(AssertionError):
            assert []
        with self.assertRaises(AssertionError):
            assert ""
        with self.assertRaises(AssertionError):
            assert 0

    def test_assert_with_expressions(self):
        def add(a, b):
            return a + b
        assert add(1, 2) == 3
        with self.assertRaises(AssertionError):
            assert add(1, 2) == 4


if __name__ == '__main__':
    unittest.main()
            
