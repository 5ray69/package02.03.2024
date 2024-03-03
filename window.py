# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import Form, Button, TextBox, Label, DialogResult
clr.AddReference('System.Drawing')
from System.Drawing import Point, Size, Font


class Window(Form):
    def __init__(self):
        self.Size = Size(700, 700)
        self.CenterToScreen()

        # метка
        self._operator = Label()
        self._operator.Text = 'Запишите в окне номера групп через \
                                запятую без пробелов в следующем виде: 1,12,1А,4,9А'
        self._operator.Size = Size(500, 200)
        self._operator.Location = Point(50,50)
        self.Controls.Add(self._operator)
        currentSize = self._operator.Font.Size
        currentSize += 4.0
        self._operator.Font = Font(self._operator.Font.Name, currentSize, 
                                    self._operator.Font.Style, self._operator.Font.Unit)

        # TextBox
        self._cell = TextBox()
        self._cell.Size = Size(200,400)
        self._cell.Location = Point(200,400)
        self.Controls.Add(self._cell)

        # кнопка OK
        self._btn_ok = Button()
        self._btn_ok.DialogResult = DialogResult.OK
        self._btn_ok.Location = Point(250,550)
        self._btn_ok.Size = Size(75, 25)
        self._btn_ok.Text = 'OK'
        self.Controls.Add(self._btn_ok)
        self.AcceptButton = self._btn_ok

        # кнопка Cancel
        self._btn_cancel = Button()
        self._btn_cancel.DialogResult = DialogResult.Cancel
        self._btn_cancel.Location = Point(self._btn_ok.Left + self._btn_ok.Width + 20, self._btn_ok.Top)
        self._btn_cancel.Size = Size(75, 25)
        self._btn_cancel.Text = 'Cancel'
        self.Controls.Add(self._btn_cancel)
        self.CancelButton = self._btn_cancel

    def input_str(self):
        return self._cell.Text

# для Dynamo
f = Window()
if f.ShowDialog() == DialogResult.OK:
    OUT = ['гр.' + let for let in f.input_str().split (',')]

# для RPS, в Dynamo это условие не будет выполняться
# if __name__ == "__main__":
#     f = Window() #создали экземпляр класса Window, экземпляр формы
#     f.ShowDialog() #чтоб при запуске данная форма появилась
#     print(f.input_str())
    







# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Windows.Forms')  # из этой библиотеки классы Form, Button, TextBox, Label, DialogResult
from System.Windows.Forms import Form, Button, TextBox, Label, DialogResult
clr.AddReference('System.Drawing')  # из этой библиотеки берем тип Point, Size, Font
from System.Drawing import Point, Size, Font


class Window(Form):
    def __init__(self):
        # форма
        self.Size = Size(700, 700)  # задали размер окна (формы)
        self.CenterToScreen()  # расположили окно (форму) по центру экрана монитора

        # метка на форме
        self._operator = Label()  # создаем метку на форме
        self._operator.Text = 'Запишите в окне номера групп через \
                                запятую без пробелов в следующем виде: 1,12,1А,4,9А'
        self._operator.Size = Size(500, 200)  # размер метки
        self._operator.Location = Point(50,50)  # от левого верхнего угла пиксели по Х и У
        self.Controls.Add(self._operator)  # добавили экземпляр класса метки в экземпляр формы
        # у метки увеличили размер шрифта
        currentSize = self._operator.Font.Size
        currentSize += 4.0
        self._operator.Font = Font(self._operator.Font.Name, currentSize, 
                                    self._operator.Font.Style, self._operator.Font.Unit)

        # ячейка ввода
        self._cell = TextBox()  # интерактивный ввод текста (ячейка ввода)
        self._cell.Size = Size(200,400)  # задали размер ячейки ввода
        self._cell.Location = Point(200,400)  # точка расположения на форме
        self.Controls.Add(self._cell)  # добавили экземпляр класса кнопки в экземпляр формы

        # кнопка OK
        self._btn_ok = Button()  # создали экземпляр класса Button, экземпляр кнопки
        self._btn_ok.DialogResult = DialogResult.OK  # перечисление DialogResult для кнопки ОК
        self._btn_ok.Location = Point(250,550)  # расположение
        self._btn_ok.Size = Size(75, 25)  # размер кнопки
        self._btn_ok.Text = 'OK'  # текст на кнопке
        self.Controls.Add(self._btn_ok)  # добавили экземпляр класса кнопки в экземпляр формы
        self.AcceptButton = self._btn_ok  # установили для кнопки accept формы значение _btn_ok

        # кнопка Cancel
        self._btn_cancel = Button()  # создали экземпляр класса Button, экземпляр кнопки
        self._btn_cancel.DialogResult = DialogResult.Cancel  # перечисление DialogResult для кнопки ОК
        self._btn_cancel.Location = Point(self._btn_ok.Left + self._btn_ok.Width + 20, self._btn_ok.Top)
        self._btn_cancel.Size = Size(75, 25)  # размер кнопки
        self._btn_cancel.Text = 'Cancel'  # текст на кнопке
        self.Controls.Add(self._btn_cancel)  # добавили экземпляр класса кнопки в экземпляр формы
        self.CancelButton = self._btn_cancel  # установили для кнопки сancel формы значение _btn_cancel

    def input_str(self):
        return self._cell.Text

# для Dynamo
f = Window()  # создали экземпляр класса Window
if f.ShowDialog() == DialogResult.OK:
    # из строки сделали список строк
    OUT = ['гр.' + let for let in f.input_str().split (',')]

# для RPS, в Dynamo это условие не будет выполняться
# if __name__ == "__main__":
#     f = Window() #создали экземпляр класса Window, экземпляр формы
#     f.ShowDialog() #чтоб при запуске данная форма появилась
#     print(f.input_str())