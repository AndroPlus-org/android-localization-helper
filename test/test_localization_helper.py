import unittest
import os
import xml.etree.ElementTree as ET
import translation_helper as localizr
import filecmp

class TestLocalizationHelperFunctions(unittest.TestCase):

    
    def setUp(self):
        # constants
        self.LANGS = ['de', 'es', 'fr','zh-rTW']

        # save cwd so we can revert back to it when we're done with a test
        self.cwd = os.getcwd()

        # get absolute path to resource directory
        self.res_path = os.path.abspath('./res')

        # get default strings tree
        self.tree = localizr.getDefaultTree(self.res_path)

    def tearDown(self):
        os.chdir(self.cwd)

    def test_writeOutMissingStrings(self):
        # get tags from default tree so we know what to write out
        tags = localizr.getTagsFromTree(self.tree)

        # get the missing keys for each lang
        keys = localizr.getKeysFromTree(self.tree)
        missing = localizr.findMissingKeys(keys, self.LANGS, self.res_path)

        # write out the files
        localizr.writeMissingKeysToFiles(self.LANGS, tags, missing, './to_translate')

        # verify that no German strings exist
        os.chdir(self.cwd)
        self.assertFalse(os.path.exists('./to_translate/strings_to_trans-de.xml'))

        # verify that spanish strings seem correct
        os.chdir(self.cwd)
        self.assertTrue(os.path.exists('./to_translate/strings_to_trans-es.xml'))
        self.assertTrue(filecmp.cmp('./test_to_translate/strings_to_trans-es.xml', './to_translate/strings_to_trans-es.xml'))

        # verify that french strings seem correct
        os.chdir(self.cwd)
        self.assertTrue(os.path.exists('./to_translate/strings_to_trans-fr.xml'))
        self.assertTrue(filecmp.cmp('./test_to_translate/strings_to_trans-fr.xml', './to_translate/strings_to_trans-fr.xml'))

        # verify that traditional chinese strings seem correct
        os.chdir(self.cwd)
        self.assertTrue(os.path.exists('./to_translate/strings_to_trans-zh-rTW.xml'))
        self.assertTrue(filecmp.cmp('./test_to_translate/strings_to_trans-zh-rTW.xml', './to_translate/strings_to_trans-zh-rTW.xml'))

    def test_getLanguageTrees(self):
        trees = localizr.getLanguageTrees(self.LANGS, self.res_path)
        self.assertEquals(len(trees), 4)

    '''
    ' Extra strings will be removed and re-arranged to match the order of the strings
    ' in the default language
    '''
    def test_cleanTranslationFiles(self):
        # get the keys from the default language
        keys = localizr.getKeysFromTree(self.tree)

        # clean the fiels
        localizr.createOutputDir('./to_translate')
        localizr.cleanTranslationFiles(self.LANGS, keys, self.res_path)

        # verify that German strings are correctly sorted
        os.chdir(self.cwd)
        self.assertTrue(filecmp.cmp('./res/values-de/strings.xml', './test_cleaned/res/values-de/strings.xml'))

        # verify that empty spanish strings stays empty
        os.chdir(self.cwd)
        self.assertTrue(filecmp.cmp('./res/values-es/strings.xml', './test_cleaned/res/values-es/strings.xml'))

        # verify that extra french string is removed
        os.chdir(self.cwd)
        self.assertTrue(filecmp.cmp('./res/values-fr/strings.xml', './test_cleaned/res/values-fr/strings.xml'))

        # verify that extra chinese string is removed and everything else is the same
        os.chdir(self.cwd)
        self.assertTrue(filecmp.cmp('./res/values-zh-rTW/strings.xml', './test_cleaned/res/values-zh-rTW/strings.xml'))


    def test_getTagByKeyName(self):
        tags = localizr.getTagsFromTree(self.tree)

        # verify that non-existent key returns None
        result = localizr.getTagByKeyName(tags, 'doesnotexist')
        self.assertIsNone(result)

        # verify that returns correct key
        result = localizr.getTagByKeyName(tags, 'test_1')
        self.assertEqual(result.attrib['name'], 'test_1')


    '''
    ' look for missing keys in the translated values.xml files
    '''
    def test_findMissingKeys(self):
        keys = localizr.getKeysFromTree(self.tree)
        missing = localizr.findMissingKeys(keys, self.LANGS, self.res_path)

        # verify that German is not missing any tags
        self.assertEqual(missing['de'], [])

        # verify that Spanish is missing all tags
        self.assertEqual(missing['es'], ['test_1', 'test_2', 'test_3', 'test_4', 'test_5'])

        # verify that French is missing all tags (even though it has an extra tag)
        self.assertEqual(missing['fr'], ['test_1', 'test_2', 'test_3', 'test_4', 'test_5'])

        # verify that traditional Chinese is only missing one tag
        self.assertEqual(missing['zh-rTW'], ['test_5'])

    '''
    ' only get language directory in the values-** and values-**-*** format
    '''
    def test_getLangsFromDir(self):
        langs = localizr.getLangsFromDir(self.res_path)
        self.assertEqual(set(langs), set(self.LANGS))

    '''
    ' keys should not contain providers or strings marked as not translatable
    '''
    def test_getKeyFromTree(self):
        keys = localizr.getKeysFromTree(self.tree)
        self.assertEqual(keys, ['test_1', 'test_2', 'test_3', 'test_4', 'test_5'])

    def test_getTagsFromTree(self):
        tags = localizr.getTagsFromTree(self.tree)
        # should return all seven tags
        self.assertEqual(len(tags), 7)


        

if __name__ == '__main__':
    unittest.main()