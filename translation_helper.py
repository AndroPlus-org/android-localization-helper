#!/usr/bin/env python

'''
This script does two things:
1) Ouputs strings that haven't been translated in files for each language
2) Cleans up string.xml files for other languages by removing old strings and 
re-ordering the strings based on their order in the default language

Other important notes
-Should support all language codes that follow the -** or -**-*** pattern
-This ignores strings that start with "provider." or have the "translatable"
attribute set to "false"
-The output directory for the missing strings is in the current directory
-The output file names look like "strings_to_trans-**" where "**" is the language
code
'''

import sys
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import codecs
import argparse
import six

ORIG_DIR = os.getcwd()

def main(res_path, clean, out_path):
    
    # go to the resource directory and save the whole path
    os.chdir(res_path)
    res_path = os.getcwd()

    # get default keys
    tree = getDefaultTree(res_path)
    keys = getKeysFromTree(tree)
    tags = getTagsFromTree(tree)

    # get the languages that we want to translate to    
    langs = getLangsFromDir(res_path)

    # look for missing keys in each language string file
    missing = findMissingKeys(keys, langs, res_path)

    # remove old strings and sort them all in the same way
    if (clean):
        cleanTranslationFiles(langs, keys, res_path)

    # write files for missing keys for each language
    createOutputDir(out_path)
    writeMissingKeysToFiles(langs, tags, missing, out_path)

def getDefaultTree(res_path):
    os.chdir(res_path)
    os.chdir('values')
    ET.register_namespace('tools', "http://schemas.android.com/tools")
    return ET.parse('strings.xml')

def createOutputDir(out_path):
    # create output directory
    os.chdir(ORIG_DIR)
    if not os.path.exists(out_path):
        os.makedirs(out_path)        

def writeMissingKeysToFiles(langs, tags, missing, out_path):
    # write xml files for missing strings for each language
    os.chdir(ORIG_DIR)
    os.chdir(out_path)
    for lang in langs:
        # skip language if it's not missing any strings
        if (len(missing[lang]) == 0):
            continue        

        # create element tree for all the missing tags
        root = ET.Element("resources")
        for key in missing[lang]: 
            tag = getTagByKeyName(tags, key)
            root.append(tag)

        # write out the 
        f = codecs.open('strings_to_trans-%s.xml' % (lang), 'wb', 'utf-8')
        f.write(prettify(root))


def getLanguageTrees(langs, res_path):
    trees = {}
    for lang in langs:
        os.chdir(res_path)
        os.chdir('values-' + lang)
        trees[lang] = ET.parse('strings.xml')
    return trees

def cleanTranslationFiles(langs, keys, res_path):
    trees = getLanguageTrees(langs, res_path)
    for lang in trees.keys():
        tree = trees[lang]
        keys_trans = getKeysFromTree(tree)
        tags_trans = getTagsFromTree(tree)
        keys_has = []
        for key in keys:
            if key in keys_trans:
                keys_has.append(key)
        root = ET.Element("resources")
        for key in keys_has: 
            tag = getTagByKeyName(tags_trans, key)
            root.append(tag)

        # write out file
        os.chdir(res_path)
        os.chdir('values-%s' % (lang))
        f = codecs.open('strings.xml', 'wb', 'utf-8')
        f.write(prettify(root))

def getTagByKeyName(tags, key):
    for tag in tags:
        if tag.attrib['name'] == key:
            return tag

'''
Return a pretty-printed XML string for the Element.
'''
def prettify(elem):
    rough_string = ET.tostring(elem, encoding='UTF-8')
    reparsed = minidom.parseString(rough_string)
    return six.u('\n').join([line for line in reparsed.toprettyxml(indent='\t').split('\n') if line.strip()])


def findMissingKeys(keys, langs, res_path):
    missing = {}
    trees = getLanguageTrees(langs, res_path)
    for lang in trees.keys():
        tree = trees[lang]
        keys_trans = getKeysFromTree(tree)
        keys_miss = []
        for key in keys:
            if key not in keys_trans:
                keys_miss.append(key)
        missing[lang] = keys_miss
    return missing

def getLangsFromDir(res_path):
    os.chdir(res_path)
    langs = []
    for x in os.walk('.'):
        if x[0][2:].startswith('values-'):
            code = [x[0][9:]][0]
            if (len(code) == 2) or (len(code) == 6 and code[2] == '-'):
                langs += [code]
    return langs

def getKeysFromTree(tree):
    root = tree.getroot()
    keys = []
    for child in root:
        # ignore strings that can't be translated
        if ('translatable' in child.attrib.keys() and child.attrib['translatable'] == 'false'):
            continue
        # ignore providers
        if (child.attrib['name'].startswith('provider.')):
            continue
        keys.append(child.attrib['name'])
    return keys

def getTagsFromTree(tree):
    root = tree.getroot()
    keys = []
    for child in root:
        keys.append(child)
    return keys


if __name__ == '__main__':
    # parse arguments and do error checking
    parser = argparse.ArgumentParser()
    parser.add_argument('--res',
                        help='Path to the app\'s /res directory. If not specifies it assumes current directory',
                        default='.')
    parser.add_argument('--output',
                        help='Path to the output directory. If not specifies it will create a folder called to_translate in the current directory',
                        default='./to_translate')
    parser.add_argument("--clean", help="re-orders and removes strings in the translation files to match the default string ordering",
                    action="store_true")

    args = parser.parse_args()

    # run main
    main(args.res, args.clean, args.output)

