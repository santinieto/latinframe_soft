import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_channel_tables(df_1, df_2):
    """
    """
    # Saco la columna de fechas de df_2 para no tener problemas
    df_2.drop('UPDATE_DATE', axis=1, inplace=True)

    # Realizar un inner join utilizando el ID como clave de referencia
    df = pd.merge(df_1, df_2, on='CHANNEL_ID', how='left')

    # Obtengo la lista de canales
    channel_ids = df['CHANNEL_ID'].unique()

    # Para cada canal voy a hacer unos graficos
    for channel_id in channel_ids:
        df_filt = df[ df['CHANNEL_ID'] == channel_id ]

        # Obtengo el nombre del canal
        channel_name = df_filt['CHANNEL_NAME'].tolist()[0]

        # Convertir la columna 'UPDATE_DATE' a objetos de fecha
        df_filt['UPDATE_DATE'] = pd.to_datetime(df_filt['UPDATE_DATE'])

        # Crear una figura con un grid de 2x2
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))

        # Cantidad de videos subidos
        axs[0, 0].plot(df_filt['UPDATE_DATE'], df_filt['VIDEOS_COUNT'], 'bo-', markersize=5)
        axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
        axs[0, 0].tick_params(axis='x', rotation=90)
        axs[0, 0].grid()
        axs[0, 0].set_xlabel('Fecha')
        axs[0, 0].set_ylabel('Videos subidos')
        axs[0, 0].set_title(f'Videos subidos a lo largo del tiempo')

        # Histograma de suscripciones diarias
        axs[0, 1].hist(df_filt['DAILY_SUBS'])
        axs[0, 1].grid()
        axs[0, 1].set_ylabel('Ocurrencias')
        axs[0, 1].set_xlabel('Suscripciones diarias')
        axs[0, 1].set_title(f'Histograma de suscripciones diarias')

        # Gráfico de visualizaciones/suscripciones totales
        axs[1, 0].plot(df_filt['UPDATE_DATE'], df_filt['TOTAL_VIEWS'], 'bo-', markersize=5)
        axs[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
        axs[1, 0].tick_params(axis='x', rotation=90)
        axs[1, 0].grid()
        axs[1, 0].set_xlabel('Fecha')
        axs[1, 0].set_ylabel('Visualizaciones')
        axs[1, 0].set_title(f'Visualizaciones a lo largo del tiempo')

        axs[1, 1].plot(df_filt['UPDATE_DATE'], df_filt['SUBSCRIBERS'], 'ro-', markersize=5)
        axs[1, 1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
        axs[1, 1].tick_params(axis='x', rotation=90)
        axs[1, 1].grid()
        axs[1, 1].set_xlabel('Fecha')
        axs[1, 1].set_ylabel('Suscripciones')
        axs[1, 1].set_title(f'Suscripciones a lo largo del tiempo')

        # Agregar un título común en el medio arriba
        fig.suptitle(f'Estadísticas de {channel_name}', fontsize=16)

    # Muestro el plot
    plt.show()