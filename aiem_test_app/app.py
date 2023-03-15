from h2o_wave import main, app, Q, ui, on, handle_on
import ai_engine_manager
import asyncio


@app('/')
async def serve(q: Q):
    print(q.args)

    if not q.client.initialized:
        await init(q)
        await home(q)

    if q.args.table_action_dai is not None:
        await table_action_dai(q)

    if q.args.dai_new or q.args.dai_instance_1 or q.args.dai_instance_2:
        await start_dai(q)

    await q.page.save()


async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(
        box='',
        title='H2O Drive',
        theme='light',
        layouts=[
            ui.layout(
                breakpoint='xs',
                # min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', direction="column"),
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='Fake H2O Drive',
        subtitle=" ",
        image='https://www.h2o.ai/wp-content/themes/h2o2018/templates/dist/images/h2o_logo.svg',
    )
    q.client.initialized = True


async def home(q: Q):
    q.page["table"] = ui.form_card(
        box=ui.box("content", order="1"),
        items=[ui.table(
            name="drive_table",
            columns=[
                ui.table_column("name", "Name"),
                ui.table_column("type", "Type"),
                ui.table_column("size", "Size"),
                ui.table_column("last_modified", "Last Modified"),
                ui.table_column("actions", "Actions", cell_type=ui.menu_table_cell_type(name='commands', commands=[
                    ui.command(name='table_action_dai', label='Send to Driverless AI', icon='ServerProcesses'),
                    # ui.command(name='table_action_h2o3', label='Send to H2O-3', icon='ServerProcesses'),
                    # ui.command(name='delete', label='Delete', icon='Delete'),
                ])),
            ],
            rows=[
                ui.table_row(name="runnable", cells=["Churn Data", "csv", "10 GB", "2022-01-01", ""]),
                ui.table_row(name="not_runnable", cells=["Churn Folder", "Directory", "", "", ""]),
            ]
        )]
    )


async def table_action_dai(q: Q):
    q.page["meta"].side_panel = ui.side_panel(
        title="Send dataset to Driverless AI",
        items=[
            ui.text("Churn Data | csv | 10GB"),

            ui.text_l("Send to new instance"),
            ui.text("_Driverless AI will be sized automatically based on your dataset; "
                    "for more control visit [My AI Engines](https://internal.dedicated.h2o.ai/aiengines)_"),
            ui.button(name="dai_new", label="Driverless AI", caption="6 CPUs | 0 GPUs | 100 GB Memory"),

            ui.text_l("Send to existing instance"),
            ui.button(name="dai_instance_1", label="Customer Churn AutoML", caption="Paused"),
            ui.button(name="dai_instance_2", label="GPU Machine",
                      caption="6 CPUs | 2 GPUs | 100 GB Memory <br /> Running"),
            ui.button(name="dai_instance_3", label="My Small Machine",
                      caption="1 CPUs | 0 GPUs | 10 GB Memory <br /> This dataset is too large for this machine",
                      disabled=True),

        ]
    )


async def start_dai(q: Q):
    q.page["meta"].side_panel = None

    if q.args.dai_new:
        dai_engine_client = ai_engine_manager.login(
            url="https://7342183.dedicated.h2o.ai",
            token_provider=my_sync_function(q)
        ).dai_engine_client
        workspace_id = "default"
        engine_id = "my-engine1"
        engine = dai_engine_client.create_engine(
            workspace_id=workspace_id,
            engine_id=engine_id,
            version="1.10.4.3",
            cpu=10,
            gpu=0,
            memory_bytes="8Gi",
            storage_bytes="64Gi",
            max_idle_duration="3600s",
            max_running_duration="7200s"
        )

        engine.wait()
        dai = engine.connect()
        await q.page.save()
        await q.sleep(2)

    if q.args.dai_instance_1:
        q.page["meta"].dialog = ui.dialog(
            title="Resuming Driverless AI",
            items=[
                ui.progress(label="")
            ]
        )
        await q.page.save()
        await q.sleep(2)

    q.page["meta"].dialog = ui.dialog(
        title="Importing Dataset",
        items=[
            ui.progress(label="")
        ]
    )
    await q.page.save()
    await q.sleep(2)

    q.page["meta"].redirect = "https://driverless.h2o.ai"
    await q.page.save()


def my_sync_function(q: Q):
    loop = asyncio.get_event_loop()
    value = loop.run_until_complete(q.auth.ensure_fresh_token())

    return value
