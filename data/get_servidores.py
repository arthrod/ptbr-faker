import json
import os
from datetime import datetime
from pathlib import Path

from google.cloud import bigquery


def fetch_and_save_names(output_dir='data', batch_size=10000):
    """
    Streams names directly from BigQuery to a JSONL file, processing in batches
    to maintain memory efficiency while eliminating unnecessary intermediate steps.
    """
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    project_id = os.getenv('PROJECT_ID')
    if not project_id:
        raise ValueError('PROJECT_ID environment variable must be set')

    print(f'Using project ID: {project_id}')
    client = bigquery.Client(project=project_id)

    # The query itself handles deduplication and NULL filtering
    query = """
    SELECT DISTINCT
        dados.nome as nome
    FROM 
        `basedosdados.br_cgu_servidores_executivo_federal.cadastro_servidores` AS dados
    WHERE 
        dados.nome IS NOT NULL
    ORDER BY 
        dados.nome
    """

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(output_dir) / f'federal_servants_names_{timestamp}.jsonl'

        print(f'Starting query execution at {datetime.now()}')

        # Configure the query job
        job_config = bigquery.QueryJobConfig(use_query_cache=True)
        query_job = client.query(query, job_config=job_config)

        with open(output_file, 'w', encoding='utf-8') as f:
            total_processed = 0

            print('Processing results...')

            # Stream results directly to JSONL file
            for row in query_job:
                json_line = json.dumps({'nome': row.nome}, ensure_ascii=False)
                f.write(json_line + '\n')

                total_processed += 1
                if total_processed % batch_size == 0:
                    print(f'Processed {total_processed} names...')

        print(f'Successfully completed at {datetime.now()}')
        print(f'Total names processed: {total_processed}')
        print(f'Output saved to: {output_file}')

    except Exception as e:
        print(f'An error occurred: {e!s}')
        raise
    finally:
        client.close()


if __name__ == '__main__':
    try:
        fetch_and_save_names()
    except Exception as e:
        print(f'Script execution failed: {e!s}')
