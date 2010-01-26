#--------------------------------------------------------------------------
# Software:     InVesalius - Software de Reconstrucao 3D de Imagens Medicas
# Copyright:    (C) 2001  Centro de Pesquisas Renato Archer
# Homepage:     http://www.softwarepublico.gov.br
# Contact:      invesalius@cti.gov.br
# License:      GNU - GPL 2 (LICENSE.txt/LICENCA.txt)
#--------------------------------------------------------------------------
#    Este programa e software livre; voce pode redistribui-lo e/ou
#    modifica-lo sob os termos da Licenca Publica Geral GNU, conforme
#    publicada pela Free Software Foundation; de acordo com a versao 2
#    da Licenca.
#
#    Este programa eh distribuido na expectativa de ser util, mas SEM
#    QUALQUER GARANTIA; sem mesmo a garantia implicita de
#    COMERCIALIZACAO ou de ADEQUACAO A QUALQUER PROPOSITO EM
#    PARTICULAR. Consulte a Licenca Publica Geral GNU para obter mais
#    detalhes.
#--------------------------------------------------------------------------
import sys

import wx
import wx.lib.hyperlink as hl
import wx.lib.pubsub as ps

import constants as const
import gui.dialogs as dlg
import gui.widgets.foldpanelbar as fpb
import gui.widgets.colourselect as csel
import gui.widgets.platebtn as pbtn
import project as prj
import utils as utl


#INTERPOLATION_MODE_LIST = ["Cubic", "Linear", "NearestNeighbor"]
MIN_TRANSPARENCY = 0
MAX_TRANSPARENCY = 100

#############
BTN_NEW = wx.NewId()
MENU_SQUARE = wx.NewId()
MENU_CIRCLE = wx.NewId()

OP_LIST = [_("Draw"), _("Erase"), _("Threshold")]


class TaskPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        inner_panel = InnerTaskPanel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(inner_panel, 1, wx.EXPAND | wx.GROW | wx.BOTTOM | wx.RIGHT |
                  wx.LEFT, 7)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.Update()
        self.SetAutoLayout(1)

        # select mask - combo
        # mesh quality - combo?
        # apply button
        # Contour - slider
        # enable / disable Fill holes

class InnerTaskPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        default_colour = self.GetBackgroundColour()
        self.SetBackgroundColour(wx.Colour(255,255,255))
        self.SetAutoLayout(1)


        BMP_ADD = wx.Bitmap("../icons/object_add.png", wx.BITMAP_TYPE_PNG)
        BMP_ADD.SetWidth(25)
        BMP_ADD.SetHeight(25)

        # Button for creating new surface
        button_new_surface = pbtn.PlateButton(self, BTN_NEW, "", BMP_ADD, style=\
                                   pbtn.PB_STYLE_SQUARE | pbtn.PB_STYLE_DEFAULT)
        self.Bind(wx.EVT_BUTTON, self.OnButton)

        # Fixed hyperlink items
        tooltip = wx.ToolTip(_("Create 3D surface based on a mask"))
        link_new_surface = hl.HyperLinkCtrl(self, -1, "Create new 3D surface")
        link_new_surface.SetUnderlines(False, False, False)
        link_new_surface.SetColours("BLACK", "BLACK", "BLACK")
        link_new_surface.SetToolTip(tooltip)
        link_new_surface.AutoBrowse(False)
        link_new_surface.UpdateLink()
        link_new_surface.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLinkNewSurface)

        # Create horizontal sizers to represent lines in the panel
        line_new = wx.BoxSizer(wx.HORIZONTAL)
        line_new.Add(link_new_surface, 1, wx.EXPAND|wx.GROW| wx.TOP|wx.RIGHT, 4)
        line_new.Add(button_new_surface, 0, wx.ALL|wx.EXPAND|wx.GROW, 0)

        # Folde panel which contains surface properties and quality
        fold_panel = FoldPanel(self)
        fold_panel.SetBackgroundColour(default_colour)

        # Button to fold to select region task
        button_next = wx.Button(self, -1, _("Next step"))
        if sys.platform != 'win32':
            button_next.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        button_next.Bind(wx.EVT_BUTTON, self.OnButtonNextTask)

        # Add line sizers into main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(line_new, 0,wx.GROW|wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        main_sizer.Add(fold_panel, 1, wx.GROW|wx.EXPAND|wx.ALL, 5)
        main_sizer.Add(button_next, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, 5)
        main_sizer.Fit(self)

        self.SetSizer(main_sizer)
        self.Update()
        self.SetAutoLayout(1)

        self.sizer = main_sizer

    def OnButton(self, evt):
        id = evt.GetId()
        if id == BTN_NEW:
            self.OnLinkNewSurface()

    def OnButtonNextTask(self, evt):
        if evt:
            ps.Publisher().sendMessage('Fold export task')
            evt.Skip()

    def OnLinkNewSurface(self, evt=None):
        #import gui.dialogs as dlg
        dialog = dlg.NewSurfaceDialog(self, -1, _('InVesalius 3 - New surface'))
        if dialog.ShowModal() == wx.ID_OK:
            # Retrieve information from dialog
            (mask_index, surface_name, surface_quality, fill_holes,\
            keep_largest) = dialog.GetValue()

            # Retrieve information from mask
            proj = prj.Project()
            mask = proj.mask_dict[mask_index]

            # Send all information so surface can be created
            surface_data = [proj.imagedata,
                            mask.colour,
                            mask.threshold_range,
                            mask.edited_points,
                            False, # overwrite
                            surface_name,
                            surface_quality,
                            fill_holes,
                            keep_largest]

            ps.Publisher().sendMessage('Create surface', surface_data)
            print "TODO: Send Signal - Create 3d surface %s \n" % surface_data
            dialog.Destroy()
        if evt:
            evt.Skip()


class FoldPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(50,700))
        self.SetBackgroundColour(wx.Colour(0,255,0))

        inner_panel = InnerFoldPanel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(inner_panel, 1, wx.EXPAND|wx.GROW, 2)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.Update()
        self.SetAutoLayout(1)

class InnerFoldPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        default_colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUBAR)
        self.SetBackgroundColour(default_colour)

        # Fold panel and its style settings
        # FIXME: If we dont insert a value in size or if we set wx.DefaultSize,
        # the fold_panel doesnt show. This means that, for some reason, Sizer
        # is not working properly in this panel. It might be on some child or
        # parent panel. Perhaps we need to insert the item into the sizer also...
        # Study this.
        fold_panel = fpb.FoldPanelBar(self, -1, wx.DefaultPosition,
                                      (10, 140), 0,fpb.FPB_SINGLE_FOLD)

        # Fold panel style
        style = fpb.CaptionBarStyle()
        style.SetCaptionStyle(fpb.CAPTIONBAR_GRADIENT_V)
        style.SetFirstColour(default_colour)
        style.SetSecondColour(default_colour)

        # Fold 1 - Surface properties
        item = fold_panel.AddFoldPanel(_("Surface properties"), collapsed=True)
        fold_panel.ApplyCaptionStyle(item, style)
        fold_panel.AddFoldPanelWindow(item, SurfaceProperties(item), Spacing= 0,
                                      leftSpacing=0, rightSpacing=0)
        fold_panel.Expand(fold_panel.GetFoldPanel(0))

        # Fold 2 - Surface tools
        item = fold_panel.AddFoldPanel(_("Advanced options"), collapsed=True)
        fold_panel.ApplyCaptionStyle(item, style)
        fold_panel.AddFoldPanelWindow(item, SurfaceTools(item), Spacing= 0,
                                      leftSpacing=0, rightSpacing=0)

        #fold_panel.AddFoldPanelWindow(item, QualityAdjustment(item), Spacing= 0,
        #                              leftSpacing=0, rightSpacing=0)
        #fold_panel.Expand(fold_panel.GetFoldPanel(1))

        # Panel sizer to expand fold panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(fold_panel, 1, wx.GROW|wx.EXPAND)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.Update()
        self.SetAutoLayout(1)

BTN_LARGEST = wx.NewId()
BTN_SPLIT = wx.NewId()
BTN_SEEDS = wx.NewId()
class SurfaceTools(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(50,400))
        default_colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUBAR)
        self.SetBackgroundColour(default_colour)

        #self.SetBackgroundColour(wx.Colour(255,255,255))
        self.SetAutoLayout(1)


        # Fixed hyperlink items
        tooltip = wx.ToolTip(_("Automatically select largest disconnect surface"))
        link_largest = hl.HyperLinkCtrl(self, -1, _("Split largest surface"))
        link_largest.SetUnderlines(False, False, False)
        link_largest.SetColours("BLACK", "BLACK", "BLACK")
        link_largest.SetToolTip(tooltip)
        link_largest.AutoBrowse(False)
        link_largest.UpdateLink()
        link_largest.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLinkLargest)

        tooltip = wx.ToolTip(_("Automatically split surfaces into new ones"))
        link_split_all = hl.HyperLinkCtrl(self, -1,"Split all disconnect surfaces")
        link_split_all.SetUnderlines(False, False, False)
        link_split_all.SetColours("BLACK", "BLACK", "BLACK")
        link_split_all.SetToolTip(tooltip)
        link_split_all.AutoBrowse(False)
        link_split_all.UpdateLink()
        link_split_all.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLinkSplit)

        tooltip = wx.ToolTip(_("Manually insert seeds of surfaces of interest"))
        link_seeds = hl.HyperLinkCtrl(self,-1,_("Select surfaces of interest"))
        link_seeds.SetUnderlines(False, False, False)
        link_seeds.SetColours("BLACK", "BLACK", "BLACK")
        link_seeds.SetToolTip(tooltip)
        link_seeds.AutoBrowse(False)
        link_seeds.UpdateLink()
        link_seeds.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLinkSeed)

        # Image(s) for buttons
        BMP_LARGEST = wx.Bitmap("../icons/connectivity_largest.png", wx.BITMAP_TYPE_PNG)
        BMP_SPLIT_ALL = wx.Bitmap("../icons/connectivity_split_all.png", wx.BITMAP_TYPE_PNG)
        BMP_SEEDS = wx.Bitmap("../icons/connectivity_manual.png", wx.BITMAP_TYPE_PNG)

        bmp_list = [BMP_LARGEST, BMP_SPLIT_ALL, BMP_SEEDS]
        for bmp in bmp_list:
            bmp.SetWidth(25)
            bmp.SetHeight(25)

        # Buttons related to hyperlinks
        button_style = pbtn.PB_STYLE_SQUARE | pbtn.PB_STYLE_DEFAULT
        button_style_plus = button_style|pbtn.PB_STYLE_TOGGLE

        button_split = pbtn.PlateButton(self, BTN_SPLIT, "", BMP_SPLIT_ALL,
                                              style=button_style)
        button_largest = pbtn.PlateButton(self, BTN_LARGEST, "",
                                               BMP_LARGEST, style=button_style)
        button_seeds = pbtn.PlateButton(self, BTN_SEEDS, "",
                                            BMP_SEEDS, style=button_style_plus)
        self.button_seeds = button_seeds

        # When using PlaneButton, it is necessary to bind events from parent win
        self.Bind(wx.EVT_BUTTON, self.OnButton)

        # Tags and grid sizer for fixed items
        flag_link = wx.EXPAND|wx.GROW|wx.LEFT|wx.TOP
        flag_button = wx.EXPAND | wx.GROW

        #fixed_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=2, vgap=0)
        fixed_sizer = wx.FlexGridSizer(rows=3, cols=2, hgap=2, vgap=0)
        fixed_sizer.AddGrowableCol(0, 1)
        fixed_sizer.AddMany([ (link_largest, 1, flag_link, 3),
                              (button_largest, 0, flag_button),
                              (link_seeds, 1, flag_link, 3),
                              (button_seeds, 0, flag_button),
                              (link_split_all, 1, flag_link, 3),
                              (button_split, 0, flag_button) ])


        # Add line sizers into main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(fixed_sizer, 0, wx.GROW|wx.EXPAND|wx.TOP, 5)

        # Update main sizer and panel layout
        self.SetSizer(main_sizer)
        self.Update()
        self.SetAutoLayout(1)
        self.sizer = main_sizer

    def OnLinkLargest(self, evt):
        self.SelectLargest()

    def OnLinkSplit(self, evt):
        self.SplitSurface()
    
    def OnLinkSeed(self, evt):
        self.button_seeds.Toggle()
        self.SelectSeed()

    def OnButton(self, evt):
        id = evt.GetId()
        if id == BTN_LARGEST:
            self.SelectLargest()
        elif id == BTN_SPLIT:
            self.SplitSurface()
        else:
            self.SelectSeed()

    def SelectLargest(self):
        ps.Publisher().sendMessage('Create surface from largest region') 

    def SplitSurface(self):
        ps.Publisher().sendMessage('Split surface') 

    def SelectSeed(self):
        if self.button_seeds.IsPressed():
            self.StartSeeding()
        else:
            self.EndSeeding()

    def StartSeeding(self):
        ps.Publisher().sendMessage('Enable style', const.VOLUME_STATE_SEED)
        ps.Publisher().sendMessage('Create surface by seeding - start')

    def EndSeeding(self):
        ps.Publisher().sendMessage('Disable style', const.VOLUME_STATE_SEED)
        ps.Publisher().sendMessage('Create surface by seeding - end')



class SurfaceProperties(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(50,400))
        default_colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUBAR)
        self.SetBackgroundColour(default_colour)

        self.surface_dict = utl.TwoWaysDictionary()

        ## LINE 1

        # Combo related to mask naem
        combo_surface_name = wx.ComboBox(self, -1, "", choices= self.surface_dict.keys(),
                                     style=wx.CB_DROPDOWN|wx.CB_READONLY)
        combo_surface_name.SetSelection(0)
        if sys.platform != 'win32':
            combo_surface_name.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        combo_surface_name.Bind(wx.EVT_COMBOBOX, self.OnComboName)
        self.combo_surface_name = combo_surface_name

        # Mask colour
        button_colour= csel.ColourSelect(self, -1,colour=(0,0,255),size=(-1,22))
        button_colour.Bind(csel.EVT_COLOURSELECT, self.OnSelectColour)
        self.button_colour = button_colour

        # Sizer which represents the first line
        line1 = wx.BoxSizer(wx.HORIZONTAL)
        line1.Add(combo_surface_name, 1, wx.LEFT|wx.EXPAND|wx.GROW|wx.TOP|wx.RIGHT, 7)
        line1.Add(button_colour, 0, wx.TOP|wx.RIGHT, 7)


        ## LINE 2

        text_transparency = wx.StaticText(self, -1, _("Transparency:"))

        slider_transparency = wx.Slider(self, -1, 0, MIN_TRANSPARENCY,
                                        MAX_TRANSPARENCY,
                                        style=wx.SL_HORIZONTAL)#|wx.SL_AUTOTICKS)
        slider_transparency.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        slider_transparency.Bind(wx.EVT_SLIDER, self.OnTransparency)
        self.slider_transparency = slider_transparency


        ## MIX LINE 2 AND 3
        flag_link = wx.EXPAND|wx.GROW|wx.RIGHT
        flag_slider = wx.EXPAND | wx.GROW| wx.LEFT|wx.TOP
        flag_combo = wx.EXPAND | wx.GROW| wx.LEFT

        fixed_sizer = wx.FlexGridSizer(rows=2, cols=2, hgap=2, vgap=4)
        fixed_sizer.AddMany([ (text_transparency, 0, flag_link, 0),
                              (slider_transparency, 1, flag_slider,4)])

        # LINE 4
        #cb = wx.CheckBox(self, -1, "Fill largest surface holes")
        #cb.SetValue(True)

        # Add all lines into main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(line1, 1, wx.GROW|wx.EXPAND|wx.TOP, 10)
        sizer.Add(fixed_sizer, 0,
wx.GROW|wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM, 10)
        #sizer.Add(cb, 0, wx.GROW|wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.Update()
        self.SetAutoLayout(1)

        self.__bind_events()

    def __bind_events(self):
        ps.Publisher().subscribe(self.InsertNewSurface,
                                'Update surface info in GUI')
        ps.Publisher().subscribe(self.ChangeSurfaceName,
                                'Change surface name')
        ps.Publisher().subscribe(self.OnCloseProject, 'Close project data')

    def OnCloseProject(self, pubsub_evt):
        self.CloseProject()

    def CloseProject(self):
        n = self.combo_surface_name.GetCount()
        for i in xrange(n-1, -1, -1):
            self.combo_surface_name.Delete(i)

    def ChangeSurfaceName(self, pubsub_evt):
        index, name = pubsub_evt.data
        old_name = self.surface_dict.get_key(index)
        self.surface_dict.remove(old_name)
        self.surface_dict[name] = index
        self.combo_surface_name.SetString(index, name)
        self.combo_surface_name.Refresh()

    def InsertNewSurface(self, pubsub_evt):
        #not_update = len(pubsub_evt.data) == 5
        index = pubsub_evt.data[0]
        name = pubsub_evt.data[1]
        colour = [value*255 for value in pubsub_evt.data[2]]
        overwrite = name in self.surface_dict.keys()
        if not overwrite or not self.surface_dict:
            self.surface_dict[name] = index
            index = self.combo_surface_name.Append(name)
            self.combo_surface_name.SetSelection(index)

        transparency = 100*pubsub_evt.data[4]
        self.button_colour.SetColour(colour)
        self.slider_transparency.SetValue(transparency)

    def OnComboName(self, evt):
        surface_name = evt.GetString()
        surface_index = evt.GetSelection()
        ps.Publisher().sendMessage('Change surface selected', surface_index)

    def OnSelectColour(self, evt):
        colour = [value/255.0 for value in evt.GetValue()]
        ps.Publisher().sendMessage('Set surface colour',
                                    (self.combo_surface_name.GetSelection(),
                                    colour))

    def OnTransparency(self, evt):
        print evt.GetInt()
        transparency = evt.GetInt()/float(MAX_TRANSPARENCY)
        # FIXME: In Mac OS/X, wx.Slider (wx.Python 2.8.10) has problem on the
        # right-limit as reported on http://trac.wxwidgets.org/ticket/4555.
        # This problem is in wx.Widgets and therefore we'll simply overcome it:
        if (wx.Platform == "__WXMAC__"):
            transparency = evt.GetInt()/(0.96*float(MAX_TRANSPARENCY))
        ps.Publisher().sendMessage('Set surface transparency',
                                  (self.combo_surface_name.GetSelection(),
                                  transparency))


class QualityAdjustment(wx.Panel):
    def __init__(self, parent):
        import constants as const
        wx.Panel.__init__(self, parent, size=(50,240))
        default_colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUBAR)
        self.SetBackgroundColour(default_colour)

        # LINE 1

        combo_quality = wx.ComboBox(self, -1, "", choices=const.SURFACE_QUALITY.keys(),
                                     style=wx.CB_DROPDOWN|wx.CB_READONLY)
        combo_quality.SetSelection(3)
        combo_quality.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        #combo_quality.Bind(wx.EVT_COMBOBOX, self.OnComboQuality)

        # LINE 2
        check_decimate = wx.CheckBox(self, -1, "")

        text_decimate = wx.StaticText(self, -1, _("Decimate resolution:"))

        spin_decimate = wx.SpinCtrl(self, -1, "", (30, 50))
        spin_decimate.SetRange(1,100)
        spin_decimate.SetValue(30)
        #spin_decimate.Bind(wx.EVT_TEXT, self.OnDecimate)

        # LINE 3
        check_smooth = wx.CheckBox(self, -1, "")

        text_smooth = wx.StaticText(self, -1, _("Smooth iterations:"))

        spin_smooth = wx.SpinCtrl(self, -1, "", (30, 50))
        spin_smooth.SetRange(1,100)
        spin_smooth.SetValue(0)

        # MIXED LINE 2 AND 3
        flag_link = wx.EXPAND|wx.GROW|wx.RIGHT|wx.LEFT
        flag_slider = wx.EXPAND | wx.GROW| wx.LEFT|wx.TOP
        flag_combo = wx.EXPAND | wx.GROW| wx.LEFT

        fixed_sizer = wx.FlexGridSizer(rows=2, cols=3, hgap=2, vgap=0)
        fixed_sizer.AddMany([ (check_decimate, 0, flag_combo, 2),
                              (text_decimate, 0, flag_slider, 7),
                              (spin_decimate, 1, flag_link,14),
                              (check_smooth, 0, flag_combo, 2),
                              (text_smooth, 0, flag_slider, 7),
                              (spin_smooth, 1, flag_link, 14)])
        fixed_sizer.AddGrowableCol(2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(combo_quality, 1, wx.EXPAND|wx.GROW|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        sizer.Add(fixed_sizer, 0, wx.LEFT|wx.RIGHT, 5)
        sizer.Fit(self)

        self.SetSizer(sizer)
        self.Update()
        self.SetAutoLayout(1)

    def OnComboQuality(self, evt):
        print "TODO: Send Signal - Change surface quality: %s" % (evt.GetString())

    def OnDecimate(self, evt):
        print "TODO: Send Signal - Decimate: %s" % float(self.spin.GetValue())/100
