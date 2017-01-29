#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: KodiHelper
# Created on: 13.01.2017

import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import json

class KodiHelper:
    """Consumes all the configuration data from Kodi as well as turns data into lists of folders and videos"""

    msl_service_server_certificate = 'Cr0CCAMSEOVEukALwQ8307Y2+LVP+0MYh/HPkwUijgIwggEKAoIBAQDm875btoWUbGqQD8eAGuBlGY+Pxo8YF1LQR+Ex0pDONMet8EHslcZRBKNQ/09RZFTP0vrYimyYiBmk9GG+S0wB3CRITgweNE15cD33MQYyS3zpBd4z+sCJam2+jj1ZA4uijE2dxGC+gRBRnw9WoPyw7D8RuhGSJ95OEtzg3Ho+mEsxuE5xg9LM4+Zuro/9msz2bFgJUjQUVHo5j+k4qLWu4ObugFmc9DLIAohL58UR5k0XnvizulOHbMMxdzna9lwTw/4SALadEV/CZXBmswUtBgATDKNqjXwokohncpdsWSauH6vfS6FXwizQoZJ9TdjSGC60rUB2t+aYDm74cIuxAgMBAAE6EHRlc3QubmV0ZmxpeC5jb20SgAOE0y8yWw2Win6M2/bw7+aqVuQPwzS/YG5ySYvwCGQd0Dltr3hpik98WijUODUr6PxMn1ZYXOLo3eED6xYGM7Riza8XskRdCfF8xjj7L7/THPbixyn4mULsttSmWFhexzXnSeKqQHuoKmerqu0nu39iW3pcxDV/K7E6aaSr5ID0SCi7KRcL9BCUCz1g9c43sNj46BhMCWJSm0mx1XFDcoKZWhpj5FAgU4Q4e6f+S8eX39nf6D6SJRb4ap7Znzn7preIvmS93xWjm75I6UBVQGo6pn4qWNCgLYlGGCQCUm5tg566j+/g5jvYZkTJvbiZFwtjMW5njbSRwB3W4CrKoyxw4qsJNSaZRTKAvSjTKdqVDXV/U5HK7SaBA6iJ981/aforXbd2vZlRXO/2S+Maa2mHULzsD+S5l4/YGpSt7PnkCe25F+nAovtl/ogZgjMeEdFyd/9YMYjOS4krYmwp3yJ7m9ZzYCQ6I8RQN4x/yLlHG5RH/+WNLNUs6JAZ0fFdCmw='
    """str: MSL service certificate"""

    msl_service_server_url = 'http://localhost:%PORT%'
    """str: MSL service url"""

    msl_service_port = 8000
    """str: MSL service port (TODO: Make it dynamic)"""

    def __init__ (self, plugin_handle, base_url):
        """Fetches all needed info from Kodi & configures the baseline of the plugin

        Parameters
        ----------
        plugin_handle : :obj:`int`
            Plugin handle

        base_url : :obj:`str`
            Plugin base url
        """
        self.plugin_handle = plugin_handle
        self.base_url = base_url
        self.addon = xbmcaddon.Addon()
        self.plugin = self.addon.getAddonInfo('name')
        self.base_data_path = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        self.home_path = xbmc.translatePath('special://home')
        self.plugin_path = self.addon.getAddonInfo('path')
        self.cookie_path = self.base_data_path + 'COOKIE'
        self.data_path = self.base_data_path + 'DATA'
        self.config_path = os.path.join(self.base_data_path, 'config')
        self.verb_log = self.addon.getSetting('logging') == 'true'
        self.default_fanart = self.addon.getAddonInfo('fanart')
        self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        self.library = None

    def refresh (self):
        """Refrsh the current list"""
        return xbmc.executebuiltin('Container.Refresh')

    def show_rating_dialog (self):
        """Asks the user for a movie rating

        Returns
        -------
        :obj:`int`
            Movie rating between 0 & 10
        """
        dlg = xbmcgui.Dialog()
        return dlg.numeric(heading=self.get_local_string(string_id=30019) + ' ' + self.get_local_string(string_id=30022), type=0)

    def show_adult_pin_dialog (self):
        """Asks the user for the adult pin

        Returns
        -------
        :obj:`int`
            4 digit adult pin needed for adult movies
        """
        dlg = xbmcgui.Dialog()
        return dlg.input(self.get_local_string(string_id=30002), type=xbmcgui.INPUT_NUMERIC)

    def show_search_term_dialog (self):
        """Asks the user for a term to query the netflix search for

        Returns
        -------
        term : :obj:`str`
            Term to search for
        """
        dlg = xbmcgui.Dialog()
        return dlg.input(self.get_local_string(string_id=30003), type=xbmcgui.INPUT_ALPHANUM)

    def show_password_dialog (self):
        """Asks the user for its Netflix password

        Returns
        -------
        :obj:`str`
            Netflix password
        """
        dlg = xbmcgui.Dialog()
        return dlg.input(self.get_local_string(string_id=30004), type=xbmcgui.INPUT_ALPHANUM)

    def show_email_dialog (self):
        """Asks the user for its Netflix account email

        Returns
        -------
        term : :obj:`str`
            Netflix account email
        """
        dlg = xbmcgui.Dialog()
        return dlg.input(self.get_local_string(string_id=30005), type=xbmcgui.INPUT_ALPHANUM)

    def show_wrong_adult_pin_notification (self):
        """Shows notification that a wrong adult pin was given

        Returns
        -------
        bool
            Dialog shown
        """
        dialog = xbmcgui.Dialog()
        dialog.notification(self.get_local_string(string_id=30006), self.get_local_string(string_id=30007), xbmcgui.NOTIFICATION_ERROR, 5000)
        return True

    def show_login_failed_notification (self):
        """Shows notification that the login failed

        Returns
        -------
        bool
            Dialog shown
        """
        dialog = xbmcgui.Dialog()
        dialog.notification(self.get_local_string(string_id=30008), self.get_local_string(string_id=30009), xbmcgui.NOTIFICATION_ERROR, 5000)
        return True

    def show_missing_inputstream_addon_notification (self):
        """Shows notification that the inputstream addon couldn't be found

        Returns
        -------
        bool
            Dialog shown
        """
        dialog = xbmcgui.Dialog()
        dialog.notification(self.get_local_string(string_id=30028), self.get_local_string(string_id=30029), xbmcgui.NOTIFICATION_ERROR, 5000)
        return True

    def set_setting (key, value):
        """Public interface for the addons setSetting method

        Returns
        -------
        bool
            Setting could be set or not
        """
        return self.addon.setSetting(key, value)

    def get_credentials (self):
        """Returns the users stored credentials

        Returns
        -------
        :obj:`dict` of :obj:`str`
            The users stored account data
        """
        return {
            'email': self.addon.getSetting('email'),
            'password': self.addon.getSetting('password')
        }

    def get_custom_library_settings (self):
        """Returns the settings in regards to the custom library folder(s)

        Returns
        -------
        :obj:`dict` of :obj:`str`
            The users library settings
        """
        return {
            'enablelibraryfolder': self.addon.getSetting('enablelibraryfolder'),
            'customlibraryfolder': self.addon.getSetting('customlibraryfolder')
        }

    def set_main_menu_selection (self, type):
        self.win.setProperty('main_menu_selection', type)

    def get_main_menu_selection (self):
        return self.win.getProperty('main_menu_selection')

    def build_profiles_listing (self, profiles, action, build_url):
        """Builds the profiles list Kodi screen

        Parameters
        ----------
        profiles : :obj:`dict` of :obj:`str`
            List of user profiles

        action : :obj:`str`
            Action paramter to build the subsequent routes

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        for profile_id in profiles:
            profile = profiles[profile_id]
            url = build_url({'action': action, 'profile_id': profile_id})
            li = xbmcgui.ListItem(label=profile['profileName'], iconImage=profile['avatar'])
            li.setProperty('fanart_image', self.default_fanart)
            xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url, listitem=li, isFolder=True)
            xbmcplugin.addSortMethod(handle=self.plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def build_main_menu_listing (self, video_list_ids, user_list_order, actions, build_url):
        """Builds the video lists (my list, continue watching, etc.) Kodi screen

        Parameters
        ----------
        video_list_ids : :obj:`dict` of :obj:`str`
            List of video lists

        user_list_order : :obj:`list` of :obj:`str`
            Ordered user lists, to determine what should be displayed in the main menue

        actions : :obj:`dict` of :obj:`str`
            Dictionary of actions to build subsequent routes

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        preselect_items = []
        for category in user_list_order:
            for video_list_id in video_list_ids['user']:
                if video_list_ids['user'][video_list_id]['name'] == category:
                    label = video_list_ids['user'][video_list_id]['displayName']
                    if category == 'netflixOriginals':
                        label = label.capitalize()
                    li = xbmcgui.ListItem(label=label)
                    li.setProperty('fanart_image', self.default_fanart)
                    # determine action route
                    action = actions['default']
                    if category in actions.keys():
                        action = actions[category]
                    # determine if the item should be selected
                    preselect_items.append((False, True)[category == self.get_main_menu_selection()])
                    url = build_url({'action': action, 'video_list_id': video_list_id, 'type': category})
                    xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url, listitem=li, isFolder=True)

        # add recommendations/genres as subfolders (save us some space on the home page)
        i18n_ids = {
            'recommendations': self.get_local_string(30001),
            'genres': self.get_local_string(30010)
        }
        for type in i18n_ids.keys():
            # determine if the lists have contents
            if len(video_list_ids[type]) > 0:
                # determine action route
                action = actions['default']
                if type in actions.keys():
                    action = actions[type]
                # determine if the item should be selected
                preselect_items.append((False, True)[type == self.get_main_menu_selection()])
                li_rec = xbmcgui.ListItem(label=i18n_ids[type])
                li_rec.setProperty('fanart_image', self.default_fanart)
                url_rec = build_url({'action': action, 'type': type})
                xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url_rec, listitem=li_rec, isFolder=True)

        # add search as subfolder
        action = actions['default']
        if 'search' in actions.keys():
            action = actions[type]
        li_rec = xbmcgui.ListItem(label=self.get_local_string(30011))
        li_rec.setProperty('fanart_image', self.default_fanart)
        url_rec = build_url({'action': action, 'type': 'search'})
        xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url_rec, listitem=li_rec, isFolder=True)

        # no srting & close
        xbmcplugin.addSortMethod(handle=self.plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.endOfDirectory(self.plugin_handle)

        # (re)select the previously selected main menu entry
        idx = 1
        preselected_list_item = None
        for item in preselect_items:
            idx += 1
            if item:
                preselected_list_item = idx
        if self.get_main_menu_selection() == 'search':
            preselected_list_item = idx + 2
        if preselected_list_item != None:
            xbmc.executebuiltin('SetFocus(%s, %s)' % (self.win.getFocusId(), preselected_list_item))

        return True

    def build_video_listing (self, video_list, actions, type, build_url):
        """Builds the video lists (my list, continue watching, etc.) contents Kodi screen

        Parameters
        ----------
        video_list_ids : :obj:`dict` of :obj:`str`
            List of video lists

        actions : :obj:`dict` of :obj:`str`
            Dictionary of actions to build subsequent routes

        type : :obj:`str`
            None or 'queue' f.e. when it´s a special video lists

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        for video_list_id in video_list:
            video = video_list[video_list_id]
            if type != 'queue' or (type == 'queue' and video['in_my_list'] == True):
                li = xbmcgui.ListItem(label=video['title'])
                # add some art to the item
                li = self._generate_art_info(entry=video, li=li)
                # it´s a show, so we need a subfolder & route (for seasons)
                isFolder = True
                url = build_url({'action': actions[video['type']], 'show_id': video_list_id})
                # lists can be mixed with shows & movies, therefor we need to check if its a movie, so play it right away
                if video_list[video_list_id]['type'] == 'movie':
                    # it´s a movie, so we need no subfolder & a route to play it
                    isFolder = False
                    # check maturity index, to determine if we need the adult pin
                    needs_pin = (True, False)[int(video['maturity']['level']) >= 1000]
                    url = build_url({'action': 'play_video', 'video_id': video_list_id, 'pin': needs_pin})
                # add list item info
                li = self._generate_entry_info(entry=video, li=li)
                li = self._generate_context_menu_items(entry=video, li=li)
                xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url, listitem=li, isFolder=isFolder)

        xbmcplugin.addSortMethod(handle=self.plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def build_search_result_listing (self, video_list, actions, build_url):
        """Builds the search results list Kodi screen

        Parameters
        ----------
        video_list : :obj:`dict` of :obj:`str`
            List of videos or shows

        actions : :obj:`dict` of :obj:`str`
            Dictionary of actions to build subsequent routes

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        return self.build_video_listing(video_list=video_list, actions=actions, type='search', build_url=build_url)

    def build_no_seasons_available (self):
        """Builds the season list screen if no seasons could be found

        Returns
        -------
        bool
            List could be build
        """
        li = xbmcgui.ListItem(label=self.get_local_string(30012))
        xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url='', listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def build_no_search_results_available (self, build_url, action):
        """Builds the search results screen if no matches could be found

        Parameters
        ----------
        action : :obj:`str`
            Action paramter to build the subsequent routes

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        li = xbmcgui.ListItem(label=self.get_local_string(30013))
        xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=build_url({'action': action}), listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def build_user_sub_listing (self, video_list_ids, type, action, build_url):
        """Builds the video lists screen for user subfolders (genres & recommendations)

        Parameters
        ----------
        video_list_ids : :obj:`dict` of :obj:`str`
            List of video lists

        type : :obj:`str`
            List type (genre or recommendation)

        action : :obj:`str`
            Action paramter to build the subsequent routes

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        for video_list_id in video_list_ids:
            li = xbmcgui.ListItem(video_list_ids[video_list_id]['displayName'])
            li.setProperty('fanart_image', self.default_fanart)
            url = build_url({'action': action, 'video_list_id': video_list_id})
            xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.addSortMethod(handle=self.plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def build_season_listing (self, seasons_sorted, season_list, build_url):
        """Builds the season list screen for a show

        Parameters
        ----------
        seasons_sorted : :obj:`list` of :obj:`str`
            Sorted season indexes

        season_list : :obj:`dict` of :obj:`str`
            List of season entries

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        for index in seasons_sorted:
            for season_id in season_list:
                season = season_list[season_id]
                if int(season['shortName'].split(' ')[1]) == index:
                    li = xbmcgui.ListItem(label=season['text'])
                    # add some art to the item
                    li = self._generate_art_info(entry=season, li=li)
                    # add list item info
                    li = self._generate_entry_info(entry=season, li=li, base_info={'mediatype': 'season'})
                    li = self._generate_context_menu_items(entry=season, li=li)
                    url = build_url({'action': 'episode_list', 'season_id': season_id})
                    xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.addSortMethod(handle=self.plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def build_episode_listing (self, episodes_sorted, episode_list, build_url):
        """Builds the episode list screen for a season of a show

        Parameters
        ----------
        episodes_sorted : :obj:`list` of :obj:`str`
            Sorted episode indexes

        episode_list : :obj:`dict` of :obj:`str`
            List of episode entries

        build_url : :obj:`fn`
            Function to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        for index in episodes_sorted:
            for episode_id in episode_list:
                episode = episode_list[episode_id]
                if int(episode['episode']) == index:
                    li = xbmcgui.ListItem(label=episode['title'])
                    # add some art to the item
                    li = self._generate_art_info(entry=episode, li=li)
                    # add list item info
                    li = self._generate_entry_info(entry=episode, li=li, base_info={'mediatype': 'episode'})
                    li = self._generate_context_menu_items(entry=episode, li=li)
                    # check maturity index, to determine if we need the adult pin
                    needs_pin = (True, False)[int(episode['maturity']['rating']['maturityLevel']) >= 1000]
                    url = build_url({'action': 'play_video', 'video_id': episode_id, 'pin': needs_pin, 'start_offset': episode['bookmark']})
                    xbmcplugin.addDirectoryItem(handle=self.plugin_handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.addSortMethod(handle=self.plugin_handle, sortMethod=xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.endOfDirectory(self.plugin_handle)
        return True

    def play_item (self, esn, video_id, start_offset=-1):
        """Plays a video

        Parameters
        ----------
        esn : :obj:`str`
            ESN needed for Widevine/Inputstream

        video_id : :obj:`str`
            ID of the video that should be played

        start_offset : :obj:`str`
            Offset to resume playback from (in seconds)

        Returns
        -------
        bool
            List could be build
        """
        inputstream_addon = self.get_inputstream_addon()
        if inputstream_addon == None:
            self.show_missing_inputstream_addon_notification()
            self.log(msg='Inputstream addon not found')
            return False

        # inputstream addon properties
        msl_service_url = self.msl_service_server_url.replace('%PORT%', str(self.msl_service_port))
        play_item = xbmcgui.ListItem(path=msl_service_url + '/manifest?id=' + video_id)
        play_item.setProperty(inputstream_addon + '.license_type', 'com.widevine.alpha')
        play_item.setProperty(inputstream_addon + '.manifest_type', 'mpd')
        play_item.setProperty(inputstream_addon + '.license_key', msl_service_url + '/license?id=' + video_id + '||b{SSM}!b{SID}|')
        play_item.setProperty(inputstream_addon + '.server_certificate', self.msl_service_server_certificate)
        play_item.setProperty('inputstreamaddon', inputstream_addon)

        # check if we have a bookmark e.g. start offset position
        if int(start_offset) > 0:
            play_item.setProperty('StartOffset', str(start_offset))
        return xbmcplugin.setResolvedUrl(self.plugin_handle, True, listitem=play_item)

    def _generate_art_info (self, entry, li):
        """Adds the art info from an entry to a Kodi list item

        Parameters
        ----------
        entry : :obj:`dict` of :obj:`str`
            Entry that should be turned into a list item

        li : :obj:`XMBC.ListItem`
            Kodi list item instance

        Returns
        -------
        :obj:`XMBC.ListItem`
            Kodi list item instance
        """
        art = {'fanart': self.default_fanart}
        if 'boxarts' in dict(entry).keys():
            art.update({
                'poster': entry['boxarts']['big'],
                'landscape': entry['boxarts']['big'],
                'thumb': entry['boxarts']['small'],
                'fanart': entry['boxarts']['big']
            })
        if 'interesting_moment' in dict(entry).keys():
            art.update({
                'poster': entry['interesting_moment'],
                'fanart': entry['interesting_moment']
            })
        if 'thumb' in dict(entry).keys():
            art.update({'thumb': entry['thumb']})
        if 'fanart' in dict(entry).keys():
            art.update({'fanart': entry['fanart']})
        if 'poster' in dict(entry).keys():
            art.update({'poster': entry['poster']})
        li.setArt(art)
        return li

    def _generate_entry_info (self, entry, li, base_info={}):
        """Adds the item info from an entry to a Kodi list item

        Parameters
        ----------
        entry : :obj:`dict` of :obj:`str`
            Entry that should be turned into a list item

        li : :obj:`XMBC.ListItem`
            Kodi list item instance

        base_info : :obj:`dict` of :obj:`str`
            Additional info that overrules the entry info

        Returns
        -------
        :obj:`XMBC.ListItem`
            Kodi list item instance
        """
        infos = base_info
        entry_keys = entry.keys()
        if 'cast' in entry_keys and len(entry['cast']) > 0:
            infos.update({'cast': entry['cast']})
        if 'creators' in entry_keys and len(entry['creators']) > 0:
            infos.update({'writer': entry['creators'][0]})
        if 'directors' in entry_keys and len(entry['directors']) > 0:
            infos.update({'director': entry['directors'][0]})
        if 'genres' in entry_keys and len(entry['genres']) > 0:
            infos.update({'genre': entry['genres'][0]})
        if 'maturity' in entry_keys:
            if 'mpaa' in entry_keys:
                infos.update({'mpaa': entry['mpaa']})
            else:
                infos.update({'mpaa': str(entry['maturity']['board']) + '-' + str(entry['maturity']['value'])})
        if 'rating' in entry_keys:
            infos.update({'rating': int(entry['rating']) * 2})
        if 'synopsis' in entry_keys:
            infos.update({'plot': entry['synopsis']})
        if 'plot' in entry_keys:
            infos.update({'plot': entry['plot']})
        if 'runtime' in entry_keys:
            infos.update({'duration': entry['runtime']})
        if 'duration' in entry_keys:
            infos.update({'duration': entry['duration']})
        if 'seasons_label' in entry_keys:
            infos.update({'season': entry['seasons_label']})
        if 'season' in entry_keys:
            infos.update({'season': entry['season']})
        if 'title' in entry_keys:
            infos.update({'title': entry['title']})
        if 'type' in entry_keys:
            if entry['type'] == 'movie' or entry['type'] == 'episode':
                li.setProperty('IsPlayable', 'true')
        if 'mediatype' in entry_keys:
            if entry['mediatype'] == 'movie' or entry['mediatype'] == 'episode':
                li.setProperty('IsPlayable', 'true')
                infos.update({'mediatype': entry['mediatype']})
        if 'watched' in entry_keys:
            infos.update({'playcount': (1, 0)[entry['watched']]})
        if 'index' in entry_keys:
            infos.update({'episode': entry['index']})
        if 'episode' in entry_keys:
            infos.update({'episode': entry['episode']})
        if 'year' in entry_keys:
            infos.update({'year': entry['year']})
        if 'quality' in entry_keys:
            quality = {'width': '960', 'height': '540'}
            if entry['quality'] == '720':
                quality = {'width': '1280', 'height': '720'}
            if entry['quality'] == '1080':
                quality = {'width': '1920', 'height': '1080'}
            li.addStreamInfo('video', quality)
        li.setInfo('video', infos)
        return li

    def _generate_context_menu_items (self, entry, li):
        """Adds context menue items to a Kodi list item

        Parameters
        ----------
        entry : :obj:`dict` of :obj:`str`
            Entry that should be turned into a list item

        li : :obj:`XMBC.ListItem`
            Kodi list item instance
        Returns
        -------
        :obj:`XMBC.ListItem`
            Kodi list item instance
        """
        items = []
        action = {}
        entry_keys = entry.keys()

        # action item templates
        url_tmpl = 'XBMC.RunPlugin(' + self.base_url + '?action=%action%&id=' + str(entry['id']) + ')'
        actions = [
            ['export_to_library', self.get_local_string(30018), 'export'],
            ['remove_from_library', self.get_local_string(30030), 'remove'],
            ['rate_on_netflix', self.get_local_string(30019), 'rating'],
            ['remove_from_my_list', self.get_local_string(30020), 'remove_from_list'],
            ['add_to_my_list', self.get_local_string(30021), 'add_to_list']
        ]

        # build concrete action items
        for action_item in actions:
            action.update({action_item[0]: [action_item[1], url_tmpl.replace('%action%', action_item[2])]})

        # add or remove the movie/show/season/episode from & to the users "My List"
        if 'in_my_list' in entry_keys:
            items.append(action['remove_from_my_list']) if entry['in_my_list'] else items.append(action['add_to_my_list'])
        elif 'queue' in entry_keys:
            items.append(action['remove_from_my_list']) if entry['queue'] else items.append(action['add_to_my_list'])
        elif 'my_list' in entry_keys:
            items.append(action['remove_from_my_list']) if entry['my_list'] else items.append(action['add_to_my_list'])
        # rate the movie/show/season/episode on Netflix
        items.append(action['rate_on_netflix'])

        # add possibility to export this movie/show/season/episode to a static/local library (and to remove it)
        # TODO: Not yet finished, still needs implementation
        #if 'type' in entry_keys:
            #items.append(action['export_to_library'])
            #items.append(action['remove_from_library'])

        # add it to the item
        li.addContextMenuItems(items)
        return li

    def log (self, msg, level=xbmc.LOGNOTICE):
        """Adds a log entry to the Kodi log

        Parameters
        ----------
        msg : :obj:`str`
            Entry that should be turned into a list item

        level : :obj:`int`
            Kodi log level
        """
        if level == xbmc.LOGDEBUG and self.verb_log:
            level = xbmc.LOGNOTICE
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        xbmc.log('[%s] %s' % (self.plugin, msg.__str__()), level)

    def get_local_string (self, string_id):
        """Returns the localized version of a string

        Parameters
        ----------
        string_id : :obj:`int`
            ID of the string that shoudl be fetched

        Returns
        -------
        :obj:`str`
            Requested string or empty string
        """
        src = xbmc if string_id < 30000 else self.addon
        locString = src.getLocalizedString(string_id)
        if isinstance(locString, unicode):
            locString = locString.encode('utf-8')
        return locString

    def get_inputstream_addon (self):
        """Checks if the inputstream addon is installed & enabled.
           Returns the type of the inputstream addon used or None if not found

        Returns
        -------
        :obj:`str` or None
            Inputstream addon or None
        """
        type = 'inputstream.adaptive'
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'Addons.GetAddonDetails',
            'params': {
                'addonid': type,
                'properties': ['enabled']
            }
        }
        response = xbmc.executeJSONRPC(json.dumps(payload))
        data = json.loads(response)
        if not 'error' in data.keys():
            if data['result']['addon']['enabled'] == True:
                return type
        return None

    def set_library (self, library):
        """Adds an instance of the Library class

        Parameters
        ----------
        library : :obj:`Library`
            instance of the Library class
        """
        self.library = library