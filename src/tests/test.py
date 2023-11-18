import unittest

import zerkel
from zerkel import *
from zerkel.interpreter.parser import ParseException
from zerkel.interpreter.semantic_analyzer import OneCompoundMismatchedArity
from zerkel.interpreter.interpreter import MismatchedNumberOfArguments


class TestSet(unittest.TestCase):
    def test_zero(self):
        zero = Set()
        self.assertEqual(0, zero.ordinal)

    def test_one(self):
        one = Set(Set())
        self.assertEqual(1, one.ordinal)

    def test_two(self):
        two = Set(Set(), Set(Set()))
        self.assertEqual(2, two.ordinal)

    def test_three(self):
        three = Set(Set(Set(Set()), Set()), Set(), Set(Set()))
        self.assertEqual(3, three.ordinal)

    def test_not_ord(self):
        s = Set(Set(), Set(Set(Set())))
        self.assertEqual(None, s.ordinal)
    
    def test_parse_zero(self):
        zero = Set.parse('{}')
        self.assertEqual(0, zero.ordinal)

    def test_parse_one(self):
        one = Set.parse('{0}')
        self.assertEqual(1, one.ordinal)

    def test_parse_two(self):
        two = Set.parse('2')
        self.assertEqual(2, two.ordinal)

    def test_parse_set(self):
        s = Set.parse('{0, 2}')
        self.assertEqual(Set(Set(), Set(Set(), Set(Set()))), s)

    def test_parse_tuple(self):
        s = Set.parse('(0, 2)')
        self.assertEqual(Set.parse('{{0}, {0, 2}}'), s)

    def test_parse_n_uplet(self):
        s = Set.parse('(0, 1, 2, 3, 4)')
        expected = Set.parse(
            '{{0}, {0, {{1}, {1, {{2}, {2, {{3}, {3, 4}}}}}}}}}'
        )
        self.assertEqual(expected, s)

    def test_generate_set(self):
        s = Set.parse('<15>')
        self.assertEqual(Set.generate(15), s)
        
    def test_generate_singleton(self):
        s = Set.generate_singleton(0)
        self.assertEqual(Set.parse('0'), s)
        s = Set.generate_singleton(4)
        self.assertEqual(Set.parse('{{{{0}}}}'), s)
        
    def test_generate_all(self):
        g = Set.generate_all(0)
        self.assertEqual((), tuple(g))
        g = Set.generate_all(1)
        self.assertEqual((Set(),), tuple(g))   
        g = Set.generate_all(2)
        e = (Set(), Set(Set()))
        self.assertEqual(e, tuple(g))   
        g = Set.generate_all(3)
        e = (Set(), Set(Set()), Set(Set(Set())))
        self.assertEqual(e, tuple(g))    
                
    def test_generate_complete(self):
        s = Set.generate_complete(0)
        self.assertEqual(Set.parse('{0}'), s)
        s = Set.generate_complete(1)
        self.assertEqual(Set.parse('{0, 1}'), s)
        s = Set.generate_complete(2)
        self.assertEqual(Set.parse('{0, 1, {1}, 2}'), s)
        s = Set.generate_complete(3)
        e = Set.parse("""{0, 1, {1}, {{1}}, 2, {2}, {0, {1}}, {0, 1, {1}}, 
                      {0, 2}, 3, {0, {1}, 2}, {0, 1, {1}, 2}, {1, {1}}, {1, 2},
                       {1, {1}, 2}, {{1}, 2}}""")
        self.assertEqual(e, s)
        
    def test_generate_random(self):
        s = Set.generate_random(0)
        self.assertEqual(0, s.rank)
        s = Set.generate_random(1)
        self.assertEqual(1, s.rank)
        s = Set.generate_random(2)
        self.assertEqual(2, s.rank)
        s = Set.generate_random(3)
        self.assertEqual(3, s.rank) 
        
    def test_generate_rank(self):
        e = (Set.parse('{{1}}'), Set.parse('{0, {1}}'), Set.parse('{1, {1}}'),
             Set.parse('{0, 1, {1}}'), Set.parse('{2}'), Set.parse('{0, 2}'),
             Set.parse('{1, 2}'), Set.parse('3'), Set.parse('{{1}, 2}'),
             Set.parse('{0, {1}, 2}'), Set.parse('{1, {1}, 2}'), 
             Set.parse('{0, 1, {1}, 2}'))
        a = tuple(Set.generate_rank(3))
        self.assertEqual(e, a)


class TestParser(unittest.TestCase):
    def test_successor(self):
        successor = parse('o+II')
        self.assertEqual(1, successor.arity)

    def test_unexpected_eof(self):
        self.assertRaises(ParseException, parse, 'o+I')

    def test_unexpected_token(self):
        self.assertRaises(ParseException, parse, 'o+III')

    def test_function(self):
        self.assertEqual(parse('o+II'), parse('successor'))

    def test_map(self):
        self.assertEqual(
            parse('oRo?<>oo+<EIo+II>>I<>I<<III'),
            parse('map successor')
        )
    
    def test_filter(self):
        self.assertEqual(
            parse('oRo?<>o?o+<EI<E<Eo+II>>I<>I<<III'),
            parse('filter successor')
        )
        
    def test_all(self):
        self.assertEqual(
            parse('o o and map equal II'),
            parse('o all equal II')
        )

class TestSemanticAnalyzer(unittest.TestCase):
    def test_mismatched_arity(self):
        ast = zerkel.parse('o+I<I')
        self.assertRaises(OneCompoundMismatchedArity, zerkel.check, ast)


class TestInterpreter(unittest.TestCase):
    def test_too_many_arguments(self):
        ast = zerkel.parse('o+II')
        self.assertRaises(
            MismatchedNumberOfArguments, zerkel.interpret, ast, '{}', '{}'
        )

    def test_not_enough_arguments(self):
        ast = zerkel.parse('o+II')
        self.assertRaises(MismatchedNumberOfArguments, zerkel.interpret, ast)

    def test_successor(self):
        ast = zerkel.parse('o+II')
        result = zerkel.interpret(ast, '{}')
        expected = Set.parse('{{}}')
        self.assertEqual(expected, result)

    def test_successor2(self):
        ast = zerkel.parse('o+II')
        result = zerkel.interpret(ast, '{{}}')
        expected = Set.parse('{{}, {{}}}')
        self.assertEqual(expected, result)

    def test_successor3(self):
        ast = zerkel.parse('o+II')
        result = zerkel.interpret(ast, '{{}, {{}}}')
        expected = Set.parse('{{}, {{}}, {{}, {{}}}}')
        self.assertEqual(expected, result)

    def test_successor4(self):
        ast = zerkel.parse('o+II')
        result = zerkel.interpret(ast, '{{}, {{}}, {{}, {{}}}}')
        expected = Set.parse(
            '{{}, {{}}, {{}, {{}}}, {{}, {{}}, {{}, {{}}}}}'
        )
        self.assertEqual(expected, result)

    def test_singleton(self):
        ast = zerkel.parse('o+>EI')
        result = zerkel.interpret(ast, '{}')
        expected = Set.parse('{{}}')
        self.assertEqual(expected, result)

    def test_singleton2(self):
        ast = zerkel.parse('o+>EI')
        result = zerkel.interpret(ast, '{{}}')
        expected = Set.parse('{{{}}}')
        self.assertEqual(expected, result)

    def test_tuple(self):
        ast = zerkel.parse('o+o+>>E>I<I')
        result = zerkel.interpret(ast, '{}', '{{}}')
        expected = Set.parse('{{}, {{}}}')
        self.assertEqual(expected, result)

    def test_closure(self):
        ast = zerkel.parse('R+')
        result = zerkel.interpret(ast, '{{}}')
        expected = Set.parse('{{}, {{}}}')
        self.assertEqual(expected, result)

    def test_closure2(self):
        ast = zerkel.parse('R+')
        result = zerkel.interpret(ast, '{{{{}}}}')
        expected = Set.parse(
            '{{}, {{}}, {{{}}}, {{{{}}}}}'
        )
        self.assertEqual(expected, result)

    def test_union(self):
        ast = zerkel.parse('oRo?<>I>>I<>I<<III')
        result = zerkel.interpret(ast, '{{{}}, {{{}}}}')
        expected = Set.parse(
            '{{}, {{}}}'
        )
        self.assertEqual(expected, result)

    def test_union2(self):
        ast = zerkel.parse('oRo?<>I>>I<>I<<III')
        result = zerkel.interpret(
            ast,
            '{{{{}}, {{{}}}}, {{}, {{}}, {{}, {{}}}, {{}, {{}}, {{}, {{}}}}}}'
        )
        expected = Set.parse(
            '{{{}}, {{{}}}, {}, {{}}, {{}, {{}}}, {{}, {{}}, {{}, {{}}}}}'
        )
        self.assertEqual(expected, result)
        
    def test_union_with_in_operator(self):
        ast = zerkel.parse('oR!<>I>>III')
        result = zerkel.interpret(
            ast,
            '{{{{}}, {{{}}}}, {{}, {{}}, {{}, {{}}}, {{}, {{}}, {{}, {{}}}}}}'
        )
        expected = Set.parse(
            '{{{}}, {{{}}}, {}, {{}}, {{}, {{}}}, {{}, {{}}, {{}, {{}}}}}'
        )
        self.assertEqual(expected, result)

    def test_rank(self):
        ast = zerkel.parse('ooRo?<>I>>I<>I<<IIIR>o+II')
        result = zerkel.interpret(
            ast,
            '{{{{}}, {{{}}}}, {{}, {{}}, {{}, {{}}}, {{}, {{}}, {{}, {{}}}}}}'
        )
        self.assertEqual(5, result.ordinal)

    def test_addition(self):
        ast = zerkel.parse('add')
        result = zerkel.interpret(ast, 8, 5)
        self.assertGreaterEqual(8 + 5, result.ordinal)

    def test_subtraction(self):
        ast = zerkel.parse('sub')
        for i in range(12):
            for j in range(12):
                result = zerkel.interpret(ast, i, j)
                self.assertEqual(max(0, i - j), result.ordinal)

    def test_division(self):
        ast = zerkel.parse('div')
        result = zerkel.interpret(ast, 3, 3)
        self.assertEqual(1, result.ordinal)
        result = zerkel.interpret(ast, 6, 3)
        self.assertEqual(2, result.ordinal)
        result = zerkel.interpret(ast, 6, 2)
        self.assertEqual(3, result.ordinal)
        result = zerkel.interpret(ast, 6, 1)
        self.assertEqual(6, result.ordinal)

    def test_log(self):
        ast = zerkel.parse('log')
        result = zerkel.interpret(ast, 4, 2)
        self.assertEqual(2, result.ordinal)

    def test_map(self):
        ast = zerkel.parse('map o+II')
        x = Set.generate(14)
        # {1, 2, {1}}
        result = zerkel.interpret(ast, x)
        expected = Set.parse('{2, 3, {1, {1}}}')
        self.assertEqual(expected, result)

    def test_multi(self):
        ast = zerkel.parse('mult')
        result = zerkel.interpret(ast, 3, 4)
        self.assertEqual(Set.generate_ordinal(3 * 4), result)

    def test_power(self):
        ast = zerkel.parse('power')
        result = zerkel.interpret(ast, 3, 2)
        self.assertEqual(Set.generate_ordinal(3 ** 2), result)

    def test_power_2(self):
        ast = zerkel.parse('power')
        result = zerkel.interpret(ast, 2, 4)
        self.assertEqual(Set.generate_ordinal(2 ** 4), result)


class TestGeneration(unittest.TestCase):
    def test_generation_successor(self):
        successor = parse('o+II')
        self.assertIn(successor, generate(4, 1))

    def test_generation_singleton(self):
        singleton = parse('o+<EI')
        self.assertIn(singleton, generate(5, 1))

    def test_generation_pair(self):
        pair = parse('o+>o+<EI<I')
        self.assertIn(pair, generate(10, 2))

    def test_generation_union(self):
        union = parse('Ro?<>I>>I<>I<<I')
        self.assertIn(union, generate(15, 2, use_in_operator=False))
        
    def test_generation_union_with_in_operator(self):
        union = parse('oR!<>I>>III')
        self.assertIn(union, generate(11, 1, use_in_operator=True))


class ExpressionTest(unittest.TestCase):
    def test_cache(self):
        node = parse('R+')
        i = Interpreter(node)
        p = ClosedExpression(Set.generate_ordinal(1), i)
        h = LazyExpression(i, node, (p,))
        self.assertIs(ClosedExpression(Set.generate_ordinal(1), i), p)
        self.assertIs(LazyExpression(i, node, (p,)), h)


if __name__ == '__main__':
    unittest.main()
