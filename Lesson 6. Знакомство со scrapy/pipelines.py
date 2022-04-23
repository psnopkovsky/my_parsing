# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['my_database']

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_hh_salary(item['salary'])
        if spider.name == 'sjru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_sj_salary(item['salary'])

        collection = self.db[spider.name]
        collection.insert_one(item)
        return item

    def process_hh_salary(self, salary):

            text = ''.join(salary)
            text = text.replace('до вычета налогов', '')

            if 'от' in text:
                if 'до' in text:
                    min_salary = salary[1].replace(u'\xa0', u'')
                    max_salary = salary[3].replace(u'\xa0', u'')
                    currency = salary[5]


                else:
                    min_salary = salary[1].replace(u'\xa0', u'')
                    max_salary = None
                    currency = salary[3]

                return min_salary, max_salary, currency
                pass

            if 'до' in text:
                min_salary = None
                max_salary = salary[1].replace(u'\xa0', u'')
                currency = salary[3].replace(u'\xa0', u'')

                return min_salary, max_salary, currency
                pass

            else:
                min_salary = None
                max_salary = None
                currency = None

                return min_salary, max_salary, currency

    def process_sj_salary(self, salary):

            text = ''.join(salary)
            text = text.replace('/месяц', '')
            text = text.replace('По договорённости', 'нет')
            text = text.replace(u'\xa0', u'')

            if 'от' in text:
                min_salary = "".join(c for c in text if c.isdigit())
                max_salary = None
                currency = text[-4:]

                return min_salary, max_salary, currency
                pass

            if 'до' in text:
                max_salary = "".join(c for c in text if c.isdigit())
                min_salary = None
                currency = text[-4:]

                return min_salary, max_salary, currency
                pass

            if text == 'нет':
                min_salary = None
                max_salary = None
                currency = None

                return min_salary, max_salary, currency
                pass


            else:

                min_max = text[:-4].split('—')

                if len(min_max) > 1:

                    min_salary = min_max[0]

                    max_salary = min_max[1]

                    currency = text[-4:]

                    return min_salary, max_salary, currency

                    pass

                else:

                    min_salary = min_max[0]

                    max_salary = min_max[0]

                    currency = text[-4:]

                    return min_salary, max_salary, currency