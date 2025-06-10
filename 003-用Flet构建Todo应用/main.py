from typing import Callable, override
import flet as ft


class Task(ft.Column):
    """
    Flet 任务类，继承自 ft.Column。

    该类用于创建一个待办事项任务，包含任务文本和复选框。
    """

    def __init__(self, name: str, on_change: Callable,  on_delete: Callable):
        super().__init__()

        # 记录变更回调函数（用于更新任务可视性）
        self.on_change: Callable = on_change

        # 记录删除回调函数（用于从主页面移除当前任务）
        self.on_delete: Callable = on_delete

        # 定义显示视图 `display_view` 所包含的控件，包含复选框、编辑按钮和删除按钮
        self.task_checkbox = ft.Checkbox(label=name,
                                         value=False,
                                         on_change=self.status_changed)
        self.edit_button = ft.IconButton(icon=ft.Icons.CREATE_OUTLINED,
                                         tooltip="Edit To-Do",
                                         on_click=self.edit_clicked)
        self.delete_button = ft.IconButton(icon=ft.Icons.DELETE_OUTLINE,
                                           tooltip="Delete To-Do",
                                           on_click=self.delete_clicked)

        # 定义显示视图
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.task_checkbox,
                ft.Row(
                    spacing=0,
                    controls=[self.edit_button, self.delete_button]
                ),
            ],
        )

        # 定义编辑视图 `edit_view` 所包含的控件，包含文本输入框和保存按钮
        self.edit_input = ft.TextField(expand=True)
        self.save_button = ft.IconButton(icon=ft.Icons.SAVE_OUTLINED,
                                         tooltip="Update To-Do",
                                         on_click=self.save_clicked)

        # 定义编辑视图
        self.edit_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.edit_input, self.save_button],
            visible=False,  # 初始时编辑视图不可见
        )

        # 设置主视图控件列表，包含显示视图和编辑视图
        self.controls = [self.display_view, self.edit_view]

    def edit_clicked(self, e: ft.ControlEvent):
        """处理编辑按钮点击事件，切换到编辑视图"""
        self.edit_input.value = self.task_checkbox.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e: ft.ControlEvent):
        """处理保存按钮点击事件，更新任务文本并切换回显示视图"""
        self.task_checkbox.label = self.edit_input.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def delete_clicked(self, e: ft.ControlEvent):
        """处理删除按钮点击事件，调用删除回调函数"""
        self.on_delete(self)

    def status_changed(self, e: ft.ControlEvent):
        """处理复选框状态变化事件，调用状态变化回调函数"""
        self.on_change(self)

    def set_visibility_by_status(self, status: str):
        """根据任务状态设置任务的可见性"""
        if status == "All":
            self.visible = True
        elif status == "Active":
            self.visible = not self.task_checkbox.value
        elif status == "Completed":
            self.visible = self.task_checkbox.value
        else:
            raise ValueError(f"Unknown status: {status}")

    @property
    def is_completed(self) -> bool:
        """检查任务是否已完成"""
        return self.task_checkbox.value


class TodoApp(ft.Column):
    """
    Flet Todo 应用程序类，继承自 ft.Column。

    该类用于创建一个简单的待办事项应用程序，允许用户添加任务并显示在页面上。
    """

    def __init__(self):
        super().__init__(expand=True) # 让根布局自适应填充页面

        # 设置宽度为600像素
        self.width = 600

        # 定义标题文本
        self.title_text = ft.Text(
            "Flet Todo App",
            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
            text_align=ft.TextAlign.CENTER,
        )

        # 定义新任务输入框
        self.new_task_input = ft.TextField(
            hint_text="What's needs to be done?",
            expand=True,
        )

        # 定义添加任务按钮
        self.add_task_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=self.add_task,
        )

        # 定义用于切换任务状态的标签页
        self.status_tabs = ft.Tabs(
            tabs=[
                ft.Tab(text="All"),
                ft.Tab(text="Active"),
                ft.Tab(text="Completed"),
            ],
            scrollable=False,
            selected_index=0,
            on_change=self.status_tabs_changed,
        )

        # 定义任务列表，初始为空，并允许滚动和自适应
        self.task_list = ft.Column(expand=True,
                                   scroll=ft.ScrollMode.ALWAYS)

        # 定义剩余任务数标签
        self.remaining_tasks_label = ft.Text("0 active task(s) remaining.")

        # 定义清空已完成任务按钮
        self.clear_completed_button = ft.OutlinedButton(
            text="Clear Completed",
            on_click=self.clear_completed_tasks,
        )

        # 定义输入视图，包含输入框和按钮
        self.input_view = ft.Row([self.new_task_input, self.add_task_button])

        # 定义任务视图，包含状态标签页、任务列表
        self.task_view = ft.Column(spacing=25,
                                   expand=True,
                                   controls=[
                                       self.status_tabs,
                                       self.task_list]
                                   )

        # 定义主视图布局
        self.controls = [
            ft.Row([self.title_text], alignment=ft.MainAxisAlignment.CENTER),
            self.input_view,
            self.task_view,
            ft.Row([self.remaining_tasks_label, self.clear_completed_button],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]

    def add_task(self, e: ft.ControlEvent):
        """添加新任务到任务列表"""
        task_name = self.new_task_input.value.strip()
        if task_name:
            task = Task(task_name, self.task_status_changed, self.delete_task)
            self.task_list.controls.append(task)
            self.new_task_input.value = ""
            self.update()

    def delete_task(self, task: Task):
        """从任务列表中删除指定任务"""
        self.task_list.controls.remove(task)
        self.update()

    def status_tabs_changed(self, e: ft.ControlEvent):
        """处理状态标签页切换事件"""
        # 将会委托 `before_update` 方法处理
        self.update()

    def task_status_changed(self, task: Task):
        """处理任务状态变化事件"""
        # 将会委托 `before_update` 方法处理
        self.update()

    def clear_completed_tasks(self, e: ft.ControlEvent):
        """清除已完成的任务"""
        for task in self.task_list.controls[:]:
            if isinstance(task, Task) and task.is_completed:
                self.delete_task(task)

    @override
    def before_update(self):
        """在更新之前执行的操作"""

        # 根据选中的标签页更新任务视图
        status = self.status_tabs.tabs[self.status_tabs.selected_index].text
        for task in self.task_list.controls:
            if isinstance(task, Task):
                task.set_visibility_by_status(status)

        # 更新剩余任务数标签
        active_tasks = sum(1 for task in self.task_list.controls
                           if isinstance(task, Task) and not task.is_completed)
        self.remaining_tasks_label.value = f"{active_tasks} active task(s) remaining."


def main(page: ft.Page):
    # 设置页面属性
    page.title = "Flet Todo App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.width = 600
    page.window.height = 700

    # 创建并添加 Todo 应用实例
    app = TodoApp()
    page.add(app)

    # 刷新页面显示
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
