import sqlite3
import luigi

from sqlalchemy import engine
import sqlalchemy
import pandas
import os
  
  
OUTPUT_DIRECTORY = 'data'
# Main DB against which the queries will be run
MAIN_DB_PATH = OUTPUT_DIRECTORY+'/IDF_CINEMA.db'
  
# Mapping of string: sqlalchemy engines to manage connections to different
# databases via the use of luigi Parameters
DB_ENGINES = {
   'eq': sqlalchemy.create_engine('sqlite:///{}'.format(MAIN_DB_PATH))
}

class SQLiteTableTarget(luigi.Target):
  
    '''Target to verify if a SQLite table exists, independant of last update'''
    def __init__(self, table: str, eng: engine.Engine):
        super().__init__()
        self._table = table
        self._eng = eng
 
   # The exists method will be checked by luigi to ensure the Tasks that
   # output this target has been completed correctly
 
    def exists(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        query_set = self._eng.execute(query.format(table_name=self._table))
        return query_set.fetchone() is not None
  
class CreateOutputDirectory(luigi.Task):
    
    task_complete = False
    
    def run(self):
        luigi.local_target.LocalFileSystem().mkdir(OUTPUT_DIRECTORY)
        self.task_complete = True
        return luigi.LocalTarget(OUTPUT_DIRECTORY)
    
    def complete(self):
        return self.task_complete
  
class CreateDB(luigi.Task):
    
    db_file_name=luigi.Parameter(default=MAIN_DB_PATH)
    task_complete = False
    
    def requires(self):
        return CreateOutputDirectory()
        
    def output(self):
        return luigi.LocalTarget(self.db_file_name)
    
    def run(self):
        with sqlite3.connect(self.db_file_name) as c:
            pass
        self.task_complete = True
        
    def complete(self):
        return self.task_complete

class GetData(luigi.Task):
       
    task_complete = False    
    engine_name = luigi.Parameter(default='eq')
 
    def requires(self):
        return CreateDB(db_file_name=MAIN_DB_PATH)
    
    def output(self):
        return SQLiteTableTarget(table='cine', eng=DB_ENGINES[self.engine_name])
    
    def run(self):
        data = pandas.read_csv(os.path.join('data-source', 'les_salles_de_cinemas_en_ile-de-france.csv'),';')
        data.to_sql('cine', con=DB_ENGINES[self.engine_name], if_exists='replace', index=False)
        self.task_complete = True
        
    def complete(self):
        return self.task_complete
       
class Top10Entrees(luigi.Task):
    
    engine_name = luigi.Parameter(default='eq')
    task_complete=False
    
    def requires(self):
        return GetData()
    
    def output(self):
        return luigi.LocalTarget(OUTPUT_DIRECTORY+"/top_10_entrees_cine_idf.csv")

    def run(self):
        top_10 = pandas.read_sql("SELECT * FROM cine ORDER BY entrees LIMIT 10",con=DB_ENGINES[self.engine_name])
        top_10.to_csv(OUTPUT_DIRECTORY+"/top_10_entrees_cine_idf.csv")
        self.task_complete=True
        
    def complete(self):
        return self.task_complete        
        
class DataFromDpt(luigi.Task):
    
    num_dpt = luigi.Parameter(default='75')
    engine_name = luigi.Parameter(default='eq')
    task_complete = False
    
    def requires(self):
        return GetData()
    
    def output(self):
        return luigi.LocalTarget(OUTPUT_DIRECTORY+"/cine_dept_%s.tsv" % self.num_dpt)
    
    def run(self):
        data_dpt = pandas.read_sql("SELECT * FROM cine WHERE dep="+self.num_dpt,con=DB_ENGINES[self.engine_name])
        data_dpt.to_csv(OUTPUT_DIRECTORY+"/cine_dept_%s.csv" % self.num_dpt)
        self.task_complete = True
        
    def complete(self):
        return self.task_complete
        
class DatasFromAllDpts(luigi.Task):
    
    engine_name = luigi.Parameter(default='eq')
    task_complete = False
    
    def requires(self):
        return GetData()
    
    def output(self):
        pass 
    
    def run(self):
        list_dpt = pandas.read_sql("SELECT DISTINCT dep FROM cine",con=DB_ENGINES[self.engine_name])
        tasks = []
        for index,row in list_dpt.iterrows():
            tasks.append(DataFromDpt(str(row['dep'])))
        yield tasks
        self.task_complete = True
        
    def complete(self):
        return self.task_complete

class allEndTasks(luigi.Task):
    
    task_complete = False
    
    def requires(self):
        return DatasFromAllDpts(),Top10Entrees()
    
    def run(self):
        self.task_complete = True
    
    def complete(self):
        return self.task_complete