import flet as ft
import pandas as pd
import threading
import time

def main(page: ft.Page):
    page.title = "Cobrança PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121316"
    page.window_width = 1150
    page.window_height = 750
    page.window_resizable = True
    page.padding = 0
    page.spacing = 0

    dados_planilha = []
    whatsapp_status = "Aguardando leitura do QR Code"
    status_color = "#EAB308"

    pagina_atual = 1
    itens_por_pagina = 10
    filtro_responsavel_val = ""
    filtro_data_val = ""

    supabase_url_val = ""
    supabase_key_val = ""

    content_area = ft.Container(expand=True, padding=25, bgcolor="#16171B")

    def salvar_configuracoes(e):
        nonlocal supabase_url_val, supabase_key_val
        supabase_url_val = input_url.value
        supabase_key_val = input_key.value

        page.snack_bar = ft.SnackBar(
            ft.Text("Configurações do Supabase salvas com sucesso!", color=ft.colors.WHITE),
            bgcolor="#22C55E"
        )
        page.snack_bar.open = True
        page.update()

    input_url = ft.TextField(
        label="Supabase URL",
        value=supabase_url_val,
        hint_text="https://seu-projeto.supabase.co",
        bgcolor="#121316",
        border_color="#2B2D37",
        border_radius=8,
        text_size=13,
        height=48
    )

    input_key = ft.TextField(
        label="Supabase Anon / Service Key",
        value=supabase_key_val,
        password=True,
        can_reveal_password=True,
        hint_text="eyJhbGciOi...",
        bgcolor="#121316",
        border_color="#2B2D37",
        border_radius=8,
        text_size=13,
        height=48
    )

    def processar_arquivo(e: ft.FilePickerResultEvent):
        nonlocal dados_planilha, pagina_atual
        if e.files:
            file_path = e.files[0].path
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                df.columns = [c.strip() for c in df.columns]
                dados_planilha = df.to_dict(orient="records")
                pagina_atual = 1

                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Planilha carregada com sucesso! {len(dados_planilha)} registros.", color=ft.colors.WHITE),
                    bgcolor="#22C55E"
                )
                page.snack_bar.open = True
                page.update()
                load_pagamentos()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Erro ao ler arquivo: {str(ex)}", color=ft.colors.WHITE),
                    bgcolor="#EF4444"
                )
                page.snack_bar.open = True
                page.update()

    file_picker = ft.FilePicker()
    file_picker.on_result = processar_arquivo
    page.overlay.append(file_picker)

    def load_dashboard(e=None):
        content_area.content = ft.Column([
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Total Arrecadado Hoje", color=ft.colors.GREY_400, size=12),
                        ft.Text("R$ 4.580,50", color="#22C55E", size=22, weight=ft.FontWeight.BOLD)
                    ]),
                    bgcolor="#1E1F25", padding=20, border_radius=12, expand=True
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Acumulado do Mês", color=ft.colors.GREY_400, size=12),
                        ft.Text("R$ 38.290,00", color="#3B82F6", size=22, weight=ft.FontWeight.BOLD)
                    ]),
                    bgcolor="#1E1F25", padding=20, border_radius=12, expand=True
                ),
            ], spacing=15),
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            ft.Text("Ações Rápidas", size=16, weight=ft.FontWeight.W_500, color=ft.colors.WHITE),
            ft.Row([
                ft.ElevatedButton(
                    "Iniciar Monitoramento Automático",
                    bgcolor="#22C55E",
                    color=ft.colors.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                ),
                ft.ElevatedButton(
                    "Processar Planilha Manualmente",
                    bgcolor="#2B2D37",
                    color=ft.colors.WHITE,
                    on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["xlsx", "xls", "csv"]),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                ),
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO, spacing=20)
        page.update()

    def load_whatsapp(e=None):
        status_text_ref = ft.Text(f"Status: {whatsapp_status}", color=status_color, size=12, weight=ft.FontWeight.BOLD)
        
        def atualizar_qr(e):
            nonlocal whatsapp_status, status_color
            whatsapp_status = "Atualizando QR Code..."
            status_color = "#3B82F6"
            status_text_ref.value = f"Status: {whatsapp_status}"
            status_text_ref.color = status_color
            page.update()
            
            def background_task():
                time.sleep(1.5)
                nonlocal whatsapp_status, status_color
                whatsapp_status = "Aguardando leitura do QR Code"
                status_color = "#EAB308"
                status_text_ref.value = f"Status: {whatsapp_status}"
                status_text_ref.color = status_color
                page.update()
            
            threading.Thread(target=background_task, daemon=True).start()

        content_area.content = ft.Column([
            ft.Text("Conexão com o WhatsApp", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text("Escaneie o QR Code abaixo com o WhatsApp do seu celular.", color=ft.colors.GREY_400, size=13),
            
            ft.ElevatedButton(
                "Gerar / Atualizar QR Code",
                bgcolor="#1D4ED8",
                color=ft.colors.WHITE,
                on_click=atualizar_qr,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
            ),
            
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("QR CODE AQUI", color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.colors.WHITE,
                            padding=40,
                            border_radius=8,
                            alignment=ft.alignment.center
                        ),
                        ft.Container(
                            content=status_text_ref,
                            bgcolor="#121316", padding=8, border_radius=6, alignment=ft.alignment.center
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                    bgcolor="#18191D", padding=25, border_radius=12, border=ft.border.all(1, "#2B2D37")
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Como conectar:", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, size=15),
                        ft.Divider(color="#2B2D37"),
                        ft.Text("1. Abra o WhatsApp no seu celular.", color=ft.colors.GREY_400, size=12),
                        ft.Text("2. Vá em Aparelhos Conectados.", color=ft.colors.GREY_400, size=12),
                        ft.Text("3. Toque em Conectar um aparelho e aponte para a tela.", color=ft.colors.GREY_400, size=12),
                        ft.Container(
                            content=ft.Text("Sua conexão é segura e criptografada.", color=ft.colors.GREY_400, size=10),
                            bgcolor="#121316", padding=10, border_radius=8
                        )
                    ], spacing=15),
                    bgcolor="#18191D", padding=20, border_radius=12, width=320, border=ft.border.all(1, "#2B2D37")
                )
            ], spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
        ], spacing=15, scroll=ft.ScrollMode.AUTO)
        page.update()

    def load_pagamentos(e=None):
        nonlocal pagina_atual, filtro_responsavel_val, filtro_data_val

        dados_filtrados = []
        for item in dados_planilha:
            resp = str(item.get('Responsável', item.get('Responsavel', ''))).lower()
            dt = str(item.get('Data', '')).lower()
            
            match_resp = filtro_responsavel_val.lower() in resp if filtro_responsavel_val else True
            match_data = filtro_data_val.lower() in dt if filtro_data_val else True
            
            if match_resp and match_data:
                dados_filtrados.append(item)

        total_itens = len(dados_filtrados)
        total_paginas = max(1, (total_itens + itens_por_pagina - 1) // itens_por_pagina)
        
        if pagina_atual > total_paginas:
            pagina_atual = total_paginas
        if pagina_atual < 1:
            pagina_atual = 1

        inicio = (pagina_atual - 1) * itens_por_pagina
        fim = inicio + itens_por_pagina
        dados_pagina = dados_filtrados[inicio:fim]

        linhas_tabela = []
        if dados_pagina:
            for item in dados_pagina:
                cliente = str(item.get('Cliente', 'N/A'))
                responsavel = str(item.get('Responsável', item.get('Responsavel', 'N/A')))
                data_pag = str(item.get('Data', 'N/A'))
                valor = str(item.get('Valor', 'N/A'))
                status = str(item.get('Status', 'Pendente'))

                linhas_tabela.append(
                    ft.Row([
                        ft.Text(cliente, color=ft.colors.WHITE, expand=2),
                        ft.Text(responsavel, color=ft.colors.WHITE, expand=2),
                        ft.Text(data_pag, color=ft.colors.GREY_300, expand=2),
                        ft.Text(valor, color=ft.colors.WHITE, expand=1),
                        ft.Container(
                            content=ft.Text(status, color="#22C55E", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor="#064E3B", padding=ft.padding.symmetric(horizontal=10, vertical=4), border_radius=6, alignment=ft.alignment.center, expand=1
                        )
                    ])
                )
        else:
            linhas_tabela.append(
                ft.Text("Nenhum registro encontrado com os filtros atuais ou planilha vazia.", color=ft.colors.GREY_400, italic=True)
            )

        txt_filtro_resp = ft.TextField(
            label="Filtrar por Responsável",
            value=filtro_responsavel_val,
            bgcolor="#121316",
            border_color="#2B2D37",
            border_radius=8,
            text_size=12,
            height=45,
            content_padding=10,
            on_change=lambda e: aplicar_filtro_resp(e.value)
        )

        txt_filtro_data = ft.TextField(
            label="Filtrar por Data",
            value=filtro_data_val,
            bgcolor="#121316",
            border_color="#2B2D37",
            border_radius=8,
            text_size=12,
            height=45,
            content_padding=10,
            on_change=lambda e: aplicar_filtro_data(e.value)
        )

        def aplicar_filtro_resp(val):
            nonlocal filtro_responsavel_val, pagina_atual
            filtro_responsavel_val = val
            pagina_atual = 1
            load_pagamentos()

        def aplicar_filtro_data(val):
            nonlocal filtro_data_val, pagina_atual
            filtro_data_val = val
            pagina_atual = 1
            load_pagamentos()

        def mudar_pagina(delta):
            nonlocal pagina_atual
            pagina_atual += delta
            load_pagamentos()

        content_area.content = ft.Column([
            ft.Text("Histórico de Pagamentos Processados", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            
            ft.Container(
                content=ft.Row([
                    ft.Container(content=txt_filtro_resp, expand=True),
                    ft.Container(content=txt_filtro_data, expand=True),
                    ft.ElevatedButton(
                        "Limpar Filtros",
                        bgcolor="#2B2D37",
                        color=ft.colors.WHITE,
                        on_click=lambda _: limpar_filtros()
                    )
                ], spacing=15),
                bgcolor="#1E1F25", padding=15, border_radius=10
            ),

            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Cliente", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400, expand=2),
                        ft.Text("Responsável", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400, expand=2),
                        ft.Text("Data", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400, expand=2),
                        ft.Text("Valor", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400, expand=1),
                        ft.Text("Status", weight=ft.FontWeight.BOLD, color=ft.colors.GREY_400, expand=1, text_align=ft.TextAlign.CENTER),
                    ]),
                    ft.Divider(color="#2B2D37"),
                    *linhas_tabela
                ], scroll=ft.ScrollMode.AUTO),
                bgcolor="#1E1F25", padding=20, border_radius=12, expand=True
            ),

            ft.Row([
                ft.Text(f"Mostrando {inicio + 1 if dados_pagina else 0} a {min(fim, total_itens)} de {total_itens} registros", color=ft.colors.GREY_400, size=12),
                ft.Row([
                    ft.ElevatedButton(
                        "Anterior",
                        bgcolor="#2B2D37",
                        color=ft.colors.WHITE,
                        disabled=pagina_atual <= 1,
                        on_click=lambda _: mudar_pagina(-1)
                    ),
                    ft.Container(
                        content=ft.Text(f"Página {pagina_atual} de {total_paginas}", color=ft.colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                        padding=10
                    ),
                    ft.ElevatedButton(
                        "Próxima",
                        bgcolor="#2B2D37",
                        color=ft.colors.WHITE,
                        disabled=pagina_atual >= total_paginas,
                        on_click=lambda _: mudar_pagina(1)
                    ),
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        ], spacing=15, expand=True)
        page.update()

    def limpar_filtros():
        nonlocal filtro_responsavel_val, filtro_data_val, pagina_atual
        filtro_responsavel_val = ""
        filtro_data_val = ""
        pagina_atual = 1
        load_pagamentos()

    def load_config(e=None):
        content_area.content = ft.Column([
            ft.Text("Configurações do Sistema", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text("Ajustes de conexão com o banco de dados Supabase e API do WhatsApp.", color=ft.colors.GREY_400, size=13),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Credenciais do Supabase", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                    ft.Divider(color="#2B2D37"),
                    input_url,
                    input_key,
                    ft.ElevatedButton(
                        "Salvar Configurações",
                        bgcolor="#22C55E",
                        color=ft.colors.WHITE,
                        on_click=salvar_configuracoes,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ], spacing=15),
                bgcolor="#1E1F25", padding=20, border_radius=12
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        page.update()

    def nav_change(e):
        index = e.control.selected_index
        if index == 0:
            load_dashboard()
        elif index == 1:
            load_whatsapp()
        elif index == 2:
            load_pagamentos()
        elif index == 3:
            load_config()

    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        bgcolor="#18191D",
        on_change=nav_change,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.CIRCLE, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.icons.CIRCLE, label="WhatsApp"),
            ft.NavigationRailDestination(icon=ft.icons.CIRCLE, label="Pagamentos"),
            ft.NavigationRailDestination(icon=ft.icons.CIRCLE, label="Configurações"),
        ],
        trailing=ft.Column([
            ft.Divider(color="#2B2D37"),
            ft.Row([
                ft.Container(bgcolor="#22C55E", width=8, height=8, border_radius=4),
                ft.Text("Status: Active", color=ft.colors.GREY_400, size=12)
            ], alignment=ft.MainAxisAlignment.START, spacing=8)
        ], alignment=ft.MainAxisAlignment.END, expand=True)
    )

    main_layout = ft.Row([
        sidebar,
        ft.VerticalDivider(width=1, color="#2B2D37"),
        content_area
    ], expand=True, spacing=0)

    page.add(main_layout)
    load_dashboard()

if __name__ == "__main__":
    ft.app(target=main)