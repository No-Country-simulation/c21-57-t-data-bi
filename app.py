import streamlit as st
import pandas as pd
from datetime import datetime
from st_keyup import st_keyup
from matplotlib import pyplot as plt
from streamlit_option_menu import option_menu
import time
import numpy as np
import streamlit.components.v1 as components

class Carrito:
    """
    Clase que representa un carrito de compras, con metodos para agregar, eliminar y obtener los items del carrito
    """
    def __init__(self):
        self.__carrito = []

    def vaciar_carrito(self):
        self.__carrito = []
        
    def agregar_item(self, item):
        self.__carrito.append(item)
    
    def eliminar_item(self, item):
        if item in self.__carrito:
            self.__carrito.remove(item)
    
    def obtener_carrito(self):
        return self.__carrito
    
class ItemCarrito:
    """
    Clase que representa un item en el carrito de compras
    """
    def __init__(self, producto,cantidad, precio_unitario, pais):
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.pais = pais
        
    def __str__(self):
        total = self.precio_unitario * self.cantidad
        return f"{self.producto} ({self.pais}) - {self.cantidad} unidades x £{self.precio_unitario:,.2f}/u = £{total:,.2f}"
        
    def calcular_total(self):
        return item.cantidad * item.precio_unitario


st.set_page_config(page_title="Analisis de abandono de carrito", 
                   layout="centered",
                   page_icon="🛒"
                   )
                   

@st.cache_resource
def load_model():
    """

    Returns:
    """
    modelo = "path" # cargar modelo como .pkl o .joblib
    return modelo

model = load_model()

@st.cache_data(show_spinner=True)
def load_data()->tuple[pd.DataFrame]:
    """
    Cargamos los datos desde archivo parquet, y los dejamos en memoria
    Returns:
        Tuple[pd.DataFrame]: Devuelve un tuple con 3 dataframes
    """
    try:
        df_canceladas = pd.read_parquet('data/silver/transacciones_canceladas.parquet')
        df_concretadas = pd.read_parquet('data/silver/transacciones_concretadas.parquet')
        df_ambas = pd.concat([df_canceladas, df_concretadas])
    except FileNotFoundError:
        st.error("No se encontraron los archivos parquet en la carpeta data/silver")
        return None, None, None
    
    return df_canceladas, df_concretadas, df_ambas

df_canceladas, df_concretadas, df_ambas = load_data()

global paises
global opciones_paises
    
paises = df_ambas['Country'].unique()
opciones_paises = paises.tolist()
opciones_paises.insert(0, 'Todos')

col1, col2 = st.columns([4, 1])
with col1:

    st.markdown(
        body="""<h1 style="text-align: center; color: #1c95cd;">Análisis de abandono de carrito</h1>""",
        unsafe_allow_html=True,
        
    )
    
with col2:    
    st.markdown(
        body="""
        <a href="https://github.com/No-Country-simulation/c21-57-t-data-bi" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="Repositorio" style="width: 50px; height: 50px; filter: invert(1); ">
        </a>
        """,
        unsafe_allow_html=True
        )

# Sidebar para seleccionar pagina
# page = st.sidebar.selectbox("Seleccione una página", ["Informacion","Consultas a df", "Visualizaciones","Resultados del Modelo"])
# Menu de opciones
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "Informacion"

menu = option_menu(menu_title=None,
                   options=["Informacion","Consultas", "Visualizaciones","Resultados del Modelo"],
                   orientation='horizontal',
                   icons=['info-circle','search','file-bar-graph-fill','robot'],
                   menu_icon='cast',
                   default_index=0,
                   styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": "#f0f2f6",  # Fondo del contenedor
                        "border-radius": "5px",
                        "border": "1px solid #dcdcdc",
                    },
                    "icon": {
                        "color": "black",  # Color de icono normal
                        "font-size": "24px",
                        "display": "block",
                        "margin-bottom": "5px"
                    },
                    "nav-link": {
                        "display": "flex",
                        "flex-direction": "column",
                        "align-items": "center",
                        "justify-content": "center",
                        "color": "#3a3a3a",  # Color de texto de los links no seleccionados
                        "font-size": "15px",
                        "padding": "12px 15px",
                        "border-radius": "5px",
                        "--hover-color": "#e0e7f3",
                        "height": "80px"
                    },
                    "nav-link-selected": {
                        "background-color": "#1c95cd",  # Fondo del link seleccionado
                        "color": "#ffffff",  # Color de texto e icono del link seleccionado
                        "border-radius": "5px",
                        "transition": "background-color 0.3s ease",
                    }
        })

st.session_state.selected_menu = menu

match menu:
    case "Informacion":
        st.write('Informacion')
        with open('README.md', 'r', encoding='utf-8') as file:
            # Ignorar las primeras 2 lineas
            for _ in range(2):
                next(file)
            readme_content = file.read()
        st.markdown(readme_content)
        
    case "Consultas":
    #Filtro de tipo de compra
        col1,col2 = st.columns([1,1])
        with col1:
            opcion = st.selectbox('Selecciona un tipo de compra', ['Ambas','Canceladas','Concretadas'])
        match opcion:
            case 'Ambas':
                df = df_ambas
            case 'Canceladas':
                df = df_canceladas
            case 'Concretadas':
                df = df_concretadas


        # Filtro de pais, DEFAULT: Todos
        with col2:
            pais = st.selectbox('Selecciona un país', opciones_paises, index=0)

        if pais in opciones_paises and pais != 'Todos':
            df = df[df['Country'] == pais]

        # Buscar transaccion especifica
        transaccion = st_keyup('Buscar Numero de transaccion',value='',debounce=500,key="1",placeholder='Buscar transaccion')

        if transaccion not in ['', None]:
            df = df[df['TransactionNo'].str.contains(transaccion.upper())]
    
        
        # Mostramos el df resultante
        with st.spinner('Cargando...'):
            st.dataframe(df)
        
        # Boton para descargar el dataframe resultante
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.download_button(label='Descargar CSV', data=df.to_csv(index=False), file_name='transacciones.csv', mime='text/csv',icon='⬇️')

        with col2:
            st.download_button(label='Descargar JSON', data=df.to_json(orient='records'), file_name='transacciones.json', mime='application/json', icon='⬇️')

    case "Visualizaciones":
        
        # MUESTRA 1 (GRAFICO 1)
        col1, col2 = st.columns([1, 1])
        with col1:   
            # Grafico de barras
            fig, ax = plt.subplots()
            df_canceladas['Country'].value_counts().plot(kind='bar', ax=ax)
            ax.set_title('Transacciones Canceladas por país')
            ax.set_xlabel('Paises')
            # mostrar el grafico
            st.pyplot(fig)
        with col2:
                
            st.write("Este grafico muestra la cantidad de transacciones canceladas por país")
            with st.expander("Codigo",expanded=True):
                code = """
                        fig, ax = plt.subplots()
                        df_canceladas['Country'].value_counts().plot(kind='bar', ax=ax)
                        ax.set_title('Transacciones Canceladas por país')
                        ax.set_xlabel('Paises')
                    """
                st.code(code, language='python')
        
        st.divider()
        
        # MUESTRA 2 (GRAFICO 2)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("Este grafico muestra la cantidad de transacciones concretadas por país")
            with st.expander("Codigo", expanded=True):
                code = """
                        fig, ax = plt.subplots()
                        df_concretadas['Country'].value_counts().plot(kind='bar', ax=ax)
                        ax.set_title('Transacciones Concretadas por país')
                        ax.set_xlabel('Paises')
                        st.pyplot(fig)
                        """
                st.code(code, language='python')
            
        with col2:
            # Grafico de barras
            fig, ax = plt.subplots()
            df_concretadas['Country'].value_counts().plot(kind='bar', ax=ax)
            ax.set_title('Transacciones Concretadas por país')
            ax.set_xlabel('Paises')
            # mostrar el grafico
            st.pyplot(fig)
        
        st.divider()       
        
        # GRAFICO 3
        # Precio x Cantidad de los productos mas comprados en un pais seleccionado
        st.write("Los 10 productos con mas £ Totales recaudadas en un país seleccionado")

        # Filtro de país
        pais_seleccionado = st.selectbox('Selecciona un país para ver los productos que mas generaron ganancias', opciones_paises)

        # Filtrar el dataframe por el país seleccionado
        if pais_seleccionado != 'Todos':
            df = df_ambas[df_ambas['Country'] == pais_seleccionado]
        else:
            df = df_ambas
        # Agrupar por producto y calcular la cantidad total comprada y el precio total
        df_productos = df.groupby('ProductName').agg({'Quantity': 'sum', 'Price': 'sum'}).reset_index()

        # Crear una nueva columna para el total recaudado (Cantidad * Precio)
        df_productos['TotalRecaudado'] = df_productos['Quantity'] * df_productos['Price']

        # Ordenar por TotalRecaudado y agarra los primeros 10
        df_productos = df_productos.sort_values(by='TotalRecaudado', ascending=False).head(10)

        with st.spinner('Cargando...'):
            fig, ax = plt.subplots()
            df_productos_sorted = df_productos.sort_values(by='TotalRecaudado', ascending=True)
            ax.barh(df_productos_sorted['ProductName'], df_productos_sorted['TotalRecaudado']) 
            ax.set_title(f'Precio £ x Cantidad: Productos que mas recaudaron de {pais_seleccionado}')
            ax.set_xlabel('$ total recaudado')
            ax.set_ylabel('Producto')       
            st.pyplot(fig)
        
        with st.expander("Codigo"):
                code = """
                        fig, ax = plt.subplots()
                        df_productos_sorted = df_productos.sort_values(by='TotalRecaudado', ascending=True)
                        ax.barh(df_productos_sorted['ProductName'], df_productos_sorted['TotalRecaudado']) 
                        ax.set_title(f'Precio x Cantidad de los productos más comprados en {pais_seleccionado}')
                        ax.set_xlabel('$ total recaudado')
                        ax.set_ylabel('Producto')       
                        st.pyplot(fig)
                        """
                st.code(code, language='python')
        
        components.iframe(
            src="" # Dashboard de PowerBI
        )
        
                            
    case "Resultados del Modelo":
            
        # st.cache_resource is the recommended way to cache global resources like ML models or database connections. 
        # Use st.cache_resource when your function returns unserializable objects that you don’t want to load multiple times. 
        # It returns the cached object itself, which is shared across all reruns and sessions without copying or duplication. 
        # If you mutate an object that is cached using st.cache_resource, that mutation will exist across all reruns and sessions.
        
        
        # Graficos del modelo
        
        
        # Carrito para predecir
        
        if not 'carrito' in st.session_state:
            st.session_state.carrito = Carrito()
            
        col1,col2 = st.columns([4,3])
        
        with col1:
            with st.form("formulario-predic"):
                st.write("Ingrese productos al carrito para predecir: ")
                
                producto_seleccionado = st.selectbox("Producto", df_ambas['ProductName'].unique())
                cantidad_productos = st.number_input("Cantidad de Productos", min_value=1, max_value=10000)
                precio_unitario = st.number_input("Precio x Unidad", min_value=1, max_value=10000)
                pais_seleccionado = st.selectbox("Pais", df_ambas['Country'].unique())
                
                item = ItemCarrito(producto_seleccionado,cantidad_productos, precio_unitario, pais_seleccionado)
                
                if st.form_submit_button("Agregar al carrito",icon='🛒',):
                    st.session_state.carrito.agregar_item(item)
                
        with col2:
            
            subcol1, subcol2 = st.columns([1, 1])
            
            with subcol1:
                st.write("Carrito de compras",)
            with subcol2:
                if st.button("Limpiar Carrito", key="limpiar",icon='🗑️'):
                    st.session_state.carrito.vaciar_carrito()
            
            if st.session_state.carrito.obtener_carrito():
                carrito = st.session_state.carrito.obtener_carrito()
                for item in carrito:
                    st.write(item)
                df = pd.DataFrame(carrito)
                
        
        if st.button("Predecir carrito", key="predict",type='primary'):
                if len(st.session_state.carrito.obtener_carrito()) == 0:
                    st.error("No hay productos en el carrito")
                else:   
                    prediccion = True 
                    st.session_state.carrito.vaciar_carrito()
                    if prediccion != 1:
                        st.error("Prediccion del Modelo: El Carrito sera cancelado")
                    else:
                        st.success("Prediccion del Modelo: El Carrito sera concretado")
                