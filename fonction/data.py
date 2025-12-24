import sqlite3 as sqlite
import pandas as pd
from sqlite3 import Error

# --- Fonctions d'Aide de Connexion Autonomes ---

def create_connection(db_file):
    """Crée une connexion à la base de données SQLite."""
    conn = None
    try:
        conn = sqlite.connect(db_file)
        if conn:
            # Bonne pratique: activer les clés étrangères
            conn.execute("PRAGMA foreign_keys = ON") 
    except Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
    return conn

def close_connection(conn):
    """Ferme la connexion à la base de données."""
    if conn:
        try:
            conn.close()
        except Error as e:
            print(f"Erreur de fermeture de la connexion: {e}")

# --- Classe Database Corrigée ---

class Database:
    def __init__(self, db_file):
        """Initialise la connexion à la base de données."""
        self.conn = create_connection(db_file)
        if self.conn is None:
            return
        self.cursor = self.conn.cursor()

    def close(self):
        """Ferme la connexion à la base de données."""
        close_connection(self.conn)
            
    def execute_query(self, query):
        """Exécute une requête (CREATE, DROP, etc.) qui ne retourne pas de données."""
        try:
            c = self.conn.cursor()
            c.execute(query)
            self.conn.commit()
        except Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")

    def fetch_data(self, query):
        """Récupère les données dans un DataFrame pandas."""
        if self.conn:
            df = pd.read_sql_query(query, self.conn)
            return df
        return pd.DataFrame()

    def insert_data(self, table, data):
        """Insère une seule ligne de données."""
        placeholders = ', '.join(['?'] * len(data))
        sql = f'INSERT INTO {table} VALUES ({placeholders})'
        try:
            cur = self.conn.cursor()
            cur.execute(sql, data)
            self.conn.commit()
            return cur.lastrowid 
        except Error as e:
            print(f"Erreur lors de l'insertion des données: {e}")
            return None

    def update_data(self, table, data, condition):
        """Met à jour les données dans une table."""
        set_clause = ', '.join([f"{k}=?" for k in data.keys()])
        sql = f'UPDATE {table} SET {set_clause} WHERE {condition}'
        try:
            cur = self.conn.cursor()
            cur.execute(sql, list(data.values()))
            self.conn.commit() 
            return cur.rowcount
        except Error as e:
            print(f"Erreur lors de la mise à jour des données: {e}")
            return 0

    def delete_data(self, table, condition):
        """Supprime les données d'une table."""
        sql = f'DELETE FROM {table} WHERE {condition}'
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            return cur.rowcount
        except Error as e:
            print(f"Erreur lors de la suppression des données: {e}")
            return 0
    
    def create_table(self, create_table_sql):
        """Crée une table."""
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(f"Erreur lors de la création de la table: {e}")

    def bulk_insert(self, table, data_list):
        """Insère en masse des données."""
        if not data_list:
            return 0
        try:
            placeholders = ', '.join(['?'] * len(data_list[0]))
            sql = f'INSERT INTO {table} VALUES ({placeholders})'
            cur = self.conn.cursor()
            cur.executemany(sql, data_list)
            self.conn.commit()
            return cur.rowcount
        except Error as e:
            print(f"Erreur lors de l'insertion en masse: {e}")
            return 0

    def fetch_all_tables(self):
        """Récupère la liste de toutes les tables."""
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return self.fetch_data(query)['name'].tolist()

    def fetch_table_schema(self, table):
        """Récupère le schéma d'une table."""
        query = f"PRAGMA table_info({table});"
        return self.fetch_data(query)

    def execute_script(self, script):
        """Exécute un script SQL."""
        try:
            c = self.conn.cursor()
            c.executescript(script)
        except Error as e:
            print(f"Erreur lors de l'exécution du script: {e}")

    def count_rows(self, table):
        """Compte le nombre de lignes dans une table."""
        query = f'SELECT COUNT(*) FROM {table};'
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            count = cur.fetchone()[0]
            return count 
        except Error as e:
            print(f"Erreur lors du comptage des lignes: {e}")
            return None

    def table_exists(self, table):
        """Vérifie si une table existe."""
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';"
        cur = self.conn.cursor()
        cur.execute(query)
        return cur.fetchone() is not None

    def drop_table(self, table):
        """Supprime une table."""
        sql = f'DROP TABLE IF EXISTS {table};'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def rename_table(self, old_name, new_name):
        """Renomme une table."""
        sql = f'ALTER TABLE {old_name} RENAME TO {new_name};'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount

    def add_column(self, table, column_definition):
        """Ajoute une colonne à une table."""
        sql = f'ALTER TABLE {table} ADD COLUMN {column_definition};'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount

    

    def list_columns(self, table):
        """Liste les colonnes d'une table."""
        query = f"PRAGMA table_info({table});"
        df = pd.read_sql_query(query, self.conn)
        return df['name'].tolist()

    def fetch_distinct_values(self, table, column):
        """Récupère les valeurs distinctes d'une colonne."""
        query = f'SELECT DISTINCT {column} FROM {table};'
        df = pd.read_sql_query(query, self.conn)
        return df[column].tolist()

    def fetch_max_value(self, table, column):
        """Récupère la valeur maximale d'une colonne."""
        query = f'SELECT MAX({column}) FROM {table};'
        return self.fetch_single_value(query)

    def fetch_min_value(self, table, column):
        """Récupère la valeur minimale d'une colonne."""
        query = f'SELECT MIN({column}) FROM {table};'
        return self.fetch_single_value(query)

    def fetch_average_value(self, table, column):
        """Récupère la valeur moyenne d'une colonne."""
        query = f'SELECT AVG({column}) FROM {table};'
        return self.fetch_single_value(query)

    def fetch_sum_value(self, table, column):
        """Récupère la somme des valeurs d'une colonne."""
        query = f'SELECT SUM({column}) FROM {table};'
        return self.fetch_single_value(query)

    def fetch_grouped_data(self, table, group_by_column, agg_column, agg_func):
        """Récupère les données regroupées avec une fonction d'agrégation."""
        query = f'SELECT {group_by_column}, {agg_func}({agg_column}) FROM {table} GROUP BY {group_by_column};'
        return self.fetch_data(query)

    def fetch_limited_data(self, table, limit):
        """Récupère un nombre limité de lignes."""
        query = f'SELECT * FROM {table} LIMIT {limit};'
        return self.fetch_data(query)

    def fetch_ordered_data(self, table, order_by_column, ascending=True):
        """Récupère les données triées."""
        order = 'ASC' if ascending else 'DESC'
        query = f'SELECT * FROM {table} ORDER BY {order_by_column} {order};'
        return self.fetch_data(query)

    def fetch_filtered_data(self, table, condition):
        """Récupère les données filtrées par une condition WHERE."""
        query = f'SELECT * FROM {table} WHERE {condition};'
        return self.fetch_data(query) 

    def fetch_joined_data(self, table1, table2, join_condition, join_type='INNER'):
        """Récupère les données issues d'une jointure."""
        query = f'SELECT * FROM {table1} {join_type} JOIN {table2} ON {join_condition};'
        return self.fetch_data(query)

    def fetch_data_with_pagination(self, table, limit, offset):
        """Récupère les données avec pagination (LIMIT et OFFSET)."""
        query = f'SELECT * FROM {table} LIMIT {limit} OFFSET {offset};'
        return self.fetch_data(query)

    # --- Méthodes SQL Avancées ---

    def fetch_data_with_subquery(self, subquery, main_query):
        """Récupère les données en utilisant une sous-requête."""
        query = f'SELECT * FROM ({subquery}) AS subquery WHERE {main_query};'
        return self.fetch_data(query)

    def fetch_data_with_cte(self, cte, main_query):
        """Récupère les données en utilisant une expression de table commune (CTE)."""
        query = f'WITH cte AS ({cte}) SELECT * FROM cte WHERE {main_query};'
        return self.fetch_data(query)

    def fetch_data_with_window_function(self, table, window_function, partition_by, order_by):
        """Récupère les données avec une fonction de fenêtre (window function)."""
        query = f'SELECT *, {window_function} OVER (PARTITION BY {partition_by} ORDER BY {order_by}) AS window_value FROM {table};'
        return self.fetch_data(query)

    def fetch_data_with_case_statement(self, table, case_statement):
        """Récupère les données avec une instruction CASE SQL."""
        query = f'SELECT *, {case_statement} AS case_value FROM {table};'
        return self.fetch_data(query)

    def fetch_data_with_union(self, query1, query2):
        """Combine deux requêtes avec UNION."""
        query = f'{query1} UNION {query2};'
        return self.fetch_data(query)

    def fetch_data_with_intersect(self, query1, query2):
        """Combine deux requêtes avec INTERSECT."""
        query = f'{query1} INTERSECT {query2};'
        return self.fetch_data(query)

    def fetch_data_with_except(self, query1, query2):
        """Combine deux requêtes avec EXCEPT (différence d'ensemble)."""
        query = f'{query1} EXCEPT {query2};'
        return self.fetch_data(query)

    def fetch_data_with_cte_recursive(self, cte, main_query):
        """Récupère les données avec une CTE récursive."""
        query = f'WITH RECURSIVE cte AS ({cte}) SELECT * FROM cte WHERE {main_query};'
        return self.fetch_data(query)

    def fetch_data_with_json_functions(self, table, json_column, json_path):
        """Récupère les données en utilisant json_extract (pour les colonnes JSON)."""
        query = f'SELECT json_extract({json_column}, \'{json_path}\') AS json_value FROM {table};'
        return self.fetch_data(query)

    def fetch_data_with_full_text_search(self, table, search_column, search_query):
        """Récupère les données avec une recherche textuelle (nécessite FTS5)."""
        query = f'SELECT * FROM {table} WHERE {search_column} MATCH \'{search_query}\';'
        return self.fetch_data(query)

    def fetch_data_with_spatial_functions(self, table, spatial_column, spatial_query):
        """Récupère les données avec une fonction spatiale (nécessite une extension comme SpatiaLite)."""
        # Note: Cette fonction suppose l'existence de l'extension SpatiaLite (ST_Intersects, GeomFromText)
        query = f'SELECT * FROM {table} WHERE ST_Intersects({spatial_column}, GeomFromText(\'{spatial_query}\'));'
        return self.fetch_data(query) 

    # --- Maintenance de la Base de Données ---

    def vacuum_database(self):
        """Réorganise la base de données (VACUUM)."""
        try:
            c = self.conn.cursor()
            c.execute("VACUUM;")
        except Error as e:
            print(f"Erreur lors de l'exécution de VACUUM: {e}")

    def analyze_database(self):
        """Collecte des statistiques sur la base de données (ANALYZE)."""
        try:
            c = self.conn.cursor()
            c.execute("ANALYZE;")
        except Error as e:
            print(f"Erreur lors de l'exécution de ANALYZE: {e}") 

    def backup_database(self, dest_file):
        """Sauvegarde la base de données courante vers un autre fichier."""
        try:
            dest_conn = sqlite.connect(dest_file)
            with dest_conn:
                self.conn.backup(dest_conn)
            dest_conn.close()
        except Error as e:
            print(f"Erreur lors de la sauvegarde: {e}") 

    def restore_database(self, source_file):
        """Restaure une base de données à partir d'un fichier source."""
        try:
            source_conn = sqlite.connect(source_file)
            with source_conn:
                source_conn.backup(self.conn)
            source_conn.close()
        except Error as e:
            print(f"Erreur lors de la restauration: {e}")

    def execute_prepared_statement(self, query, params):
        """Exécute une instruction préparée (pour l'insertion/mise à jour sécurisée)."""
        try:
            c = self.conn.cursor()
            c.execute(query, params)
            self.conn.commit()
        except Error as e:
            print(f"Erreur lors de l'exécution de l'instruction préparée: {e}") 

    def fetch_data_with_prepared_statement(self, query, params):
        """Récupère les données avec une instruction préparée."""
        # pandas.read_sql_query prend en charge les paramètres directement
        return pd.read_sql_query(query, self.conn, params=params)

    # --- Méthodes de Récupération Alternatives ---

    def fetch_data_as_dict(self, query):
        """Récupère les données sous forme de liste de dictionnaires."""
        cur = self.conn.cursor()
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        rows = cur.fetchall()
        result = [dict(zip(columns, row)) for row in rows]
        return result

    def fetch_data_as_list_of_tuples(self, query):
        """Récupère les données sous forme de liste de tuples."""
        cur = self.conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows

    def fetch_single_value(self, query):
        """Récupère une seule valeur (par exemple, un COUNT ou MAX)."""
        cur = self.conn.cursor()
        cur.execute(query)
        value = cur.fetchone()
        return value[0] if value else None

    def fetch_multiple_values(self, query):
        """Récupère une liste de valeurs de la première colonne."""
        cur = self.conn.cursor()
        cur.execute(query)
        values = cur.fetchall()
        return [value[0] for value in values]

    # --- Méthodes d'Analyse de Données (Pandas) ---

    def fetch_data_with_pivot(self, table, index_column, pivot_column, value_column):
        """Applique l'opération de pivot (transformation de ligne à colonne)."""
        query = f'SELECT {index_column}, {pivot_column}, {value_column} FROM {table};'
        df = self.fetch_data(query)
        pivot_df = df.pivot(index=index_column, columns=pivot_column, values=value_column)
        return pivot_df.reset_index()

    def fetch_data_with_melt(self, table, id_vars, value_vars):
        """Applique l'opération de melt (transformation de colonne à ligne)."""
        query = f'SELECT * FROM {table};'
        df = self.fetch_data(query)
        melt_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars)
        return melt_df

    def fetch_data_with_multi_index(self, table, index_columns):
        """Récupère les données et définit un index multiple."""
        query = f'SELECT * FROM {table};'
        df = self.fetch_data(query)
        multi_index_df = df.set_index(index_columns)
        return multi_index_df

    def fetch_data_with_time_series(self, table, date_column, value_column, freq='D'):
        """Récupère et ré-échantillonne les données pour l'analyse de séries temporelles."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        time_series_df = df.resample(freq).mean()
        return time_series_df

    def fetch_data_with_rolling_window(self, table, date_column, value_column, window_size):
        """Calcule une moyenne mobile (rolling window)."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        rolling_df = df.rolling(window=window_size).mean()
        return rolling_df

    def fetch_data_with_expanding_window(self, table, date_column, value_column): 
        """Calcule une moyenne cumulative (expanding window).""" 
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        expanding_df = df.expanding().mean()
        return expanding_df

    def fetch_data_with_resample(self, table, date_column, value_column, freq):
        """Ré-échantillonne les données de séries temporelles (agrégation)."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        resampled_df = df.resample(freq).mean()
        return resampled_df

    def fetch_data_with_shift(self, table, date_column, value_column, periods):
        """Décalage (shift) des valeurs de séries temporelles (pour lag)."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        shifted_df = df.shift(periods=periods)
        return shifted_df

    def fetch_data_with_lag(self, table, date_column, value_column, periods):
        """Calcule la valeur décalée (lag) (alias de shift)."""
        return self.fetch_data_with_shift(table, date_column, value_column, periods)

    def fetch_data_with_lead(self, table, date_column, value_column, periods):
        """Calcule la valeur avancée (lead)."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        lead_df = df.shift(periods=-periods)
        return lead_df

    def fetch_data_with_pct_change(self, table, date_column, value_column, periods):
        """Calcule le pourcentage de changement."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        pct_change_df = df.pct_change(periods=periods)
        return pct_change_df

    def fetch_data_with_diff(self, table, date_column, value_column, periods):
        """Calcule la différence entre les valeurs."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        diff_df = df.diff(periods=periods)
        return diff_df

    def fetch_data_with_autocorr(self, table, date_column, value_column, lag):
        """Calcule l'autocorrélation."""
        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        autocorr_value = df[value_column].autocorr(lag=lag)
        return autocorr_value

    def fetch_data_with_cross_correlation(self, table1, table2, date_column1, value_column1, date_column2, value_column2, lag):
        """Calcule la corrélation croisée entre deux séries temporelles."""
        query1 = f'SELECT {date_column1}, {value_column1} FROM {table1};'
        df1 = pd.read_sql_query(query1, self.conn, parse_dates=[date_column1])
        df1.set_index(date_column1, inplace=True)
        query2 = f'SELECT {date_column2}, {value_column2} FROM {table2};'
        df2 = pd.read_sql_query(query2, self.conn, parse_dates=[date_column2])
        df2.set_index(date_column2, inplace=True)
        combined_df = pd.merge(df1, df2, left_index=True, right_index=True, how='inner')
        cross_corr_value = combined_df[value_column1].corr(combined_df[value_column2].shift(lag))
        return cross_corr_value

    def fetch_data_with_time_series_anomaly_detection(self, table, date_column, value_column, threshold):
        """Détecte les anomalies dans une série temporelle à l'aide d'Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            print("Erreur: La bibliothèque scikit-learn (sklearn) est nécessaire pour cette fonction.")
            return pd.DataFrame()

        query = f'SELECT {date_column}, {value_column} FROM {table};'
        df = pd.read_sql_query(query, self.conn, parse_dates=[date_column])
        df.set_index(date_column, inplace=True)
        
        # Le seuil (threshold) est utilisé comme 'contamination' dans IsolationForest
        model = IsolationForest(contamination=threshold, random_state=42)
        df['anomaly'] = model.fit_predict(df[[value_column]])
        anomalies = df[df['anomaly'] == -1]
        return anomalies