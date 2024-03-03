# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import System.Drawing
import System.Windows.Forms


class UserFormCreateCircuitStoyak(System.Windows.Forms.Form):
    def __init__(self):
        self.Text = "Выберите к чему подключать стояки"
        self.BackColor = System.Drawing.Color.FromArgb(238, 238, 238)
        captionHeight = System.Windows.Forms.SystemInformation.CaptionHeight
        self.MinimumSize = System.Drawing.Size(550, (430 + captionHeight))
        self.CenterToScreen()
        self.dictUserSelect = {}


        # # CHECKBOX
        # self.checkBox = System.Windows.Forms.CheckBox()
        # self.checkBox.Location = System.Drawing.Point(40, 30)
        # self.checkBox.Size = System.Drawing.Size(400, 30)
        # self.checkBox.Text = "поставьте галку, если подключаем к ВРУ"
        # self.checkBox.Font = System.Drawing.Font(
        #                 'Arial',
        #                 System.Single(9),
        #                 System.Drawing.FontStyle.Bold,
        #                 System.Drawing.GraphicsUnit.Point)
        # self.Controls.Add(self.checkBox)

        # LABEL1
        self.label1 = System.Windows.Forms.Label()
        self.label1.Text = '   Внимание! Электрические цепи будут построены именно\
                            \nк тому объекту, который будет указан в этой форме.\
                            \nУбедитесь, что Вы правильно указываете имя панели.\
                            \n   Чтобы вовремя отменить действие скрипта, \
                            \nпосле построения цепей, проверьте к тому ли объекту \
                            \nбыло выполнено подключение.'
        self.label1.Font = System.Drawing.Font(
                                'Arial',
                                System.Single(9),
                                System.Drawing.FontStyle.Italic,
                                System.Drawing.GraphicsUnit.Point)
        self.label1.Location = System.Drawing.Point(40, 30)
        self.label1.Size = System.Drawing.Size(
            self.label1.PreferredWidth, self.label1.PreferredHeight)
        self.Controls.Add(self.label1)

        self.radioButtonFont = System.Drawing.Font(
                                'Arial',
                                System.Single(10),
                                System.Drawing.FontStyle.Bold,
                                System.Drawing.GraphicsUnit.Point)
        # RADIOBUTTON1
        self.radioButton1 = System.Windows.Forms.RadioButton()
        self.radioButton1.Location = System.Drawing.Point(20, 20)
        self.radioButton1.Size = System.Drawing.Size(200, 30)
        self.radioButton1.Font = self.radioButtonFont
        self.radioButton1.Text = "точка подключений"
        self.radioButton1.Checked = True

        # RADIOBUTTON2
        self.radioButton2 = System.Windows.Forms.RadioButton()
        self.radioButton2.Location = System.Drawing.Point(20, 45)
        self.radioButton2.Size = System.Drawing.Size(200, 30)
        self.radioButton2.Font = self.radioButtonFont
        self.radioButton2.Text = "точка подключений2"

        # GROUPBOX FOR RADIOBUTTON
        self.groupBox = System.Windows.Forms.GroupBox()
        self.groupBox.Controls.Add(self.radioButton2)
        self.groupBox.Controls.Add(self.radioButton1)
        self.Controls.Add(self.groupBox)
        self.groupBox.Location = System.Drawing.Point(40, 200)
        self.groupBox.Size = System.Drawing.Size(460, 80)
        self.groupBox.Text = "Выберите к какому из объектов в ВРУ выполнять подключение стояков"
        self.groupBox.Font = System.Drawing.Font(
                                'Arial',
                                System.Single(9),
                                System.Drawing.FontStyle.Bold,
                                System.Drawing.GraphicsUnit.Point)

        # LABEL2
        self.label2 = System.Windows.Forms.Label()
        self.label2.Text = 'В качестве объекта указано имя панели'
        self.label2.Font = System.Drawing.Font(
                                'Arial',
                                System.Single(9),
                                System.Drawing.FontStyle.Italic,
                                System.Drawing.GraphicsUnit.Point)
        self.label2.Location = System.Drawing.Point(
            self.groupBox.Location.X, self.groupBox.Location.Y + 80)
        self.label2.Size = System.Drawing.Size(
            self.label2.PreferredWidth, self.label2.PreferredHeight)
        self.Controls.Add(self.label2)


        self.buttonFont = System.Drawing.Font(
                                'Arial',
                                System.Single(11),
                                System.Drawing.FontStyle.Bold,
                                System.Drawing.GraphicsUnit.Point)
        # DEFINEBUTTON
        self.defineButton = System.Windows.Forms.Button()
        self.defineButton.Location = System.Drawing.Point(
                                        120, self.MinimumSize.Height - 80)
        self.defineButton.Size = System.Drawing.Size(100, 30)
        self.defineButton.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        self.defineButton.FlatAppearance.BorderSize = 0
        self.defineButton.Text = "Применить"
        self.defineButton.Font = self.buttonFont
        self.defineButton.ForeColor = System.Drawing.Color.FromName('White')
        self.defineButton.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
        self.defineButton.Anchor = (
            System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)
        self.Controls.Add(self.defineButton)

        # CANCELBUTTON
        self.cancelButton = System.Windows.Forms.Button()
        self.cancelButton.Location = System.Drawing.Point(
                            self.defineButton.Location.X + 200, self.MinimumSize.Height - 80)
        self.cancelButton.Size = System.Drawing.Size(100, 30)
        self.cancelButton.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        self.cancelButton.FlatAppearance.BorderSize = 0
        self.cancelButton.Text = "Отмена"
        self.cancelButton.Font = self.buttonFont
        self.cancelButton.ForeColor = System.Drawing.Color.FromName('White')
        self.cancelButton.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
        self.cancelButton.Anchor = (
            System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)
        self.Controls.Add(self.cancelButton)

        # BIND EVENTS TO CONTROL
        # MouseEnter Событие, когда указатель мыши заходит в пределы элемента управления
        # MouseLeave происходит, когда указатель мыши покидает элемент управления
        self.defineButton.MouseEnter += self.defineButtonMouseEnter
        self.defineButton.MouseLeave += self.defineButtonMouseLeave

        self.cancelButton.MouseEnter += self.cancelButtonMouseEnter
        self.cancelButton.MouseLeave += self.cancelButtonMouseLeave

        self.defineButton.Click += self.clickOnDefineButton
        self.cancelButton.Click += self.clickOnCancelButton

    def clickOnDefineButton(self, sender, args):
        # print(self.checkBox.Checked)
        # print(self.radioButton1.Checked)
        # print(self.radioButton2.Checked)
        userSelect = {}
        # userSelect["connectToVRY"] = self.checkBox.Checked
        if self.radioButton1.Checked:
            userSelect["objectInVRY"] = self.radioButton1.Text
        if self.radioButton2.Checked:
            userSelect["objectInVRY"] = self.radioButton2.Text
        userSelect["cancelScript"] = False
        self.dictUserSelect = userSelect

        self.Close()

    def clickOnCancelButton(self, sender, args):
        userSelect = {}
        userSelect["cancelScript"] = True
        self.dictUserSelect = userSelect

        self.Close()

    # DEFINE MOUSE ENTER EVENT
    def defineButtonMouseEnter(self, sender, args):
        self.defineButton.ForeColor = System.Drawing.Color.FromName('White')
        self.defineButton.BackColor = System.Drawing.Color.FromArgb((int(255 * .02)), 60, 90, 100)

    def defineButtonMouseLeave(self, sender, args):
        self.defineButton.ForeColor = System.Drawing.Color.FromName('White')
        self.defineButton.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)

    def cancelButtonMouseEnter(self, sender, args):
        self.cancelButton.ForeColor = System.Drawing.Color.FromName('White')
        self.cancelButton.BackColor = System.Drawing.Color.FromArgb((int(255 * .02)), 60, 90, 100)

    def cancelButtonMouseLeave(self, sender, args):
        self.cancelButton.ForeColor = System.Drawing.Color.FromName('White')
        self.cancelButton.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)


# form = UserFormCreateCircuitStoyak()
# form.ShowDialog()
