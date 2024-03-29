# -*- coding: utf-8 -*-
# module user_form_select_panel_number_shem_PIcosf.py
import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')

import System.Drawing
import System.Windows.Forms


class UserFormSelectPanelNumber(System.Windows.Forms.Form):
    def __init__(self, listPanelNumber):
        self.listPanelNumber = listPanelNumber

        self.Text = "Выберите номера панелей"
        self.BackColor = System.Drawing.Color.FromArgb(238, 238, 238)
        caption_height = System.Windows.Forms.SystemInformation.CaptionHeight
        self.MinimumSize = System.Drawing.Size(400, (450 + caption_height))
        self.CenterToScreen()

        self.listUserSelect = []

        self._list_box = System.Windows.Forms.ListBox()
        self._list_box.Size = System.Drawing.Size(200, 250)
        self._list_box.Location = System.Drawing.Point(70, 10)
        self._list_box.BorderStyle = 0
        self._list_box.Font = System.Drawing.Font(
                            'Arial', System.Single(11), System.Drawing.FontStyle.Bold)
        for panelNumber in self.listPanelNumber:
            self._list_box.Items.Add(panelNumber)
        self._list_box.SelectionMode = System.Windows.Forms.SelectionMode.MultiSimple
        self.Controls.Add(self._list_box)

        self._label = System.Windows.Forms.Label()
        self._label.Text = 'Щелчок мышью выбирает номер панели в списке.\
                            \n\
                            \nЕсли ничего не будет выбрано, \
                            \nто ни одно семейство не будет создано.\
                            \n\
                            \nЕсли номера нет в списке, то Вы его не проставили\
                            \nв параметр БУДОВА_Номер панели'
        self._label.Font = System.Drawing.Font(
                                'Arial',
                                System.Single(10.5),
                                System.Drawing.FontStyle.Italic,
                                System.Drawing.GraphicsUnit.Point)
        self._label.Location = System.Drawing.Point(
            10, self._list_box.Location.Y + self._list_box.Size.Height + 10)
        self._label.Size = System.Drawing.Size(
            self._label.PreferredWidth, self._label.PreferredHeight)
        self.Controls.Add(self._label)

        self.button_fonts = System.Drawing.Font(
                                'Arial',
                                System.Single(11),
                                System.Drawing.FontStyle.Bold,
                                System.Drawing.GraphicsUnit.Point)

        self._defin_button = System.Windows.Forms.Button()
        self._defin_button.Location = System.Drawing.Point(
                                        30, self.MinimumSize.Height - 80)
        self._defin_button.Size = System.Drawing.Size(100, 30)
        self._defin_button.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        self._defin_button.FlatAppearance.BorderSize = 0
        self._defin_button.Text = "Применить"
        self._defin_button.Font = self.button_fonts
        self._defin_button.ForeColor = System.Drawing.Color.FromName('White')
        self._defin_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
        self._defin_button.Anchor = (
            System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)
        self.Controls.Add(self._defin_button)

        self._cancel_button = System.Windows.Forms.Button()
        self._cancel_button.Location = System.Drawing.Point(
                            self._defin_button.Location.X + 150, self.MinimumSize.Height - 80)
        self._cancel_button.Size = System.Drawing.Size(100, 30)
        self._cancel_button.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        self._cancel_button.FlatAppearance.BorderSize = 0
        self._cancel_button.Text = "Отмена"
        self._cancel_button.Font = self.button_fonts
        self._cancel_button.ForeColor = System.Drawing.Color.FromName('White')
        self._cancel_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
        self._cancel_button.Anchor = (
            System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)
        self.Controls.Add(self._cancel_button)

        # BIND EVENTS TO CONTROL
        # MouseEnter Событие, когда указатель мыши заходит в пределы элемента управления
        # MouseLeave происходит, когда указатель мыши покидает элемент управления
        self._defin_button.MouseEnter += self.define_button_mouse_enter
        self._defin_button.MouseLeave += self.define_button_mouse_leave

        self._cancel_button.MouseEnter += self.cancel_button_mouse_enter
        self._cancel_button.MouseLeave += self.cancel_button_mouse_leave

        self._defin_button.Click += self._click_on_define_button
        self._cancel_button.Click += self._click_on_cancel_button

    def _click_on_define_button(self, sender, args):
        userSelect = []
        for el in self._list_box.SelectedItems:
            userSelect.append(el)
        self.listUserSelect = userSelect
        
        self.Close()

    def _click_on_cancel_button(self, sender, args):
        self.Close()

    # DEFINE MOUSE ENTER EVENT
    def define_button_mouse_enter(self, sender, args):
        self._defin_button.ForeColor = System.Drawing.Color.FromName('White')
        self._defin_button.BackColor = System.Drawing.Color.FromArgb((int(255 * .02)), 60, 90, 100)

    def define_button_mouse_leave(self, sender, args):
        self._defin_button.ForeColor = System.Drawing.Color.FromName('White')
        self._defin_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)

    def cancel_button_mouse_enter(self, sender, args):
        self._cancel_button.ForeColor = System.Drawing.Color.FromName('White')
        self._cancel_button.BackColor = System.Drawing.Color.FromArgb((int(255 * .02)), 60, 90, 100)

    def cancel_button_mouse_leave(self, sender, args):
        self._cancel_button.ForeColor = System.Drawing.Color.FromName('White')
        self._cancel_button.BackColor = System.Drawing.Color.FromArgb(255, 60, 90, 100)
