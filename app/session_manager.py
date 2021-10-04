from __future__ import annotations
from abc import ABC, abstractmethod


class SessionManager:
    def __init__(self, summoner_id: int=None) -> None:
        self.my_team: Team = MyTeam(self)
        self.actions: ActionList = ActionList(self)
        self.SUMMONER_ID: int = summoner_id
    
    def get_me_as_teammember(self) -> TeamMember:
        return self.my_team.get_me()

    def get_my_cell_id(self) -> int:
        return self.my_team.get_me().cell_id
    
    def get_summoner_id(self):
        return self.SUMMONER_ID
    
    def get_my_action(self) -> Action:
        return self.actions.get_my_action()
    
    def get_actions_in_progress(self) -> list:
        return self.actions.get_actions_in_progress()
    
    def get_action_in_progress(self) -> Action:
        return self.actions.get_action_in_progress()
    
    def get_my_champion_pick_intent(self):
        return self.my_team.get_me().champion_pick_intent
    
    def get_ban_type_actions(self) -> list:
        '''Return ActionList with all actions whose 'type' attribute
        is 'ban'.
        '''

        return self.actions.get_ban_actions()

    def get_pick_type_actions(self) -> list:
        '''Return ActionList with all actions whose 'type' attribute
        is 'pick' and all are compleated.
        '''

        return self.actions.get_pick_actions()
    
    def get_actions_with_unavailable_champions(self) -> list:
        return [*self.get_ban_type_actions(), *self.get_pick_type_actions()]
    
    # def get_my_active_action(self) -> Action:
    #     '''Try to get your active action. If your action is
    #     not active return None'''

    #     actions_in_progress: list = self.get_actions_in_progress()
    #     my_cell_id: int = self.get_my_cell_id()
    #     my_active_action: Action = None
        
    #     if actions_in_progress:
    #         action: Action
    #         for action in actions_in_progress:
    #             if my_cell_id == action.actor_cell_id:
    #                 my_active_action = action

    #     return my_active_action
    
    def set_summoner_id(self, arg_summoner_id: int):
        self.SUMMONER_ID: int = arg_summoner_id
    

class Action:
    def __init__(self) -> None:
        '''Construdtor of Action should not assign any data to attributes.'''

        self.actor_cell_id: int = None
        self.champion_id: int = None
        self.completed: bool = None
        self.id: int = None
        self.is_ally_action: bool = None
        self.is_in_progress: bool = None
        self.type: str = None

    def _update_action(self, action: dict):
        '''This method assigns data to attributes based on provided json
        file. argument should be dictionary without any nested dictionaries.'''
        
        self.actor_cell_id: int = action['actorCellId']
        self.champion_id: int = action['championId']
        self.completed: bool = action['completed']
        self.id: int = action['id']
        self.is_ally_action: bool = action['isAllyAction']
        self.is_in_progress: bool = action['isInProgress']
        self.type: str = action['type']
    

class ActionList(list):
    '''This class goal is to gather all Action objects and provide firendly
    interface to work with those objects (e.g. finding my_action).'''

    def __init__(self, arg_session_manager: SessionManager) -> None:
        self.session_manager: SessionManager = arg_session_manager

        # your summoner action which is currently in progress
        self.my_action: Action = None
        self.actions_in_progress: list = None
    
    def get_actions_in_progress(self) -> list:
        '''This method shouldn't iterate through ActionList to find actions in
        progress. The variable should be updated by syn_with_websocket and
        always be updated.'''

        return self.actions_in_progress
    
    def get_action_in_progress(self) -> Action:
        '''This method tries returns action (instead of list of actions)
        directly if list consists of one element.'''

        if (actions := self.get_actions_in_progress()):
            if len(actions) == 1:
                return actions[0]

            else:
                return None
    
    def get_my_action(self):
        '''Simirally as get_action_n_progress - it shouldn't iterate through
        ActionList.'''

        return self.my_action
    
    def get_ban_actions(self) -> list:
        return self.ban_actions
    
    def get_pick_actions(self) -> list:
        return self.pick_actions
    
    def sync_with_websocket(self, actions: list) -> None:


        # Helper iterator to keep the code clean
        iter_action = self._iter_actions(actions)

        # my_action is my action + active action
        self.my_action: Action = None
        self.actions_in_progress: list = list()
        self.ban_actions: list = list()
        self.pick_actions: list = list()

        self.clear()
        # Iterate through all team members provied by argument (list from json)
        for _action in iter_action:

            # Creagte new instance of action for each element from the lists
            new_action = Action()

            # Update attributes of this instance using helper method
            new_action._update_action(_action)
            # Update attributes of this instance using helper method
            self.append(new_action)
            
            # If newly created instance's actor_cell_id attribute is filled 
            # with data wich value is equal to your cell id of current session
            # and the action is in progress,
            # update my_action wich represents your action object in
            # session (the action part). Note that this is always checked
            # when sync occures (this is - when websocked is CREATED, UPDATED)

            # Gather all action instances wich are tagged as 'isInProgress'
            if new_action.is_in_progress:
                self.actions_in_progress.append(new_action)

                if new_action.actor_cell_id == \
                    self.session_manager.get_my_cell_id():

                    self.my_action = new_action
            
            # Append ban and pick to ban_actions and pick_action respectively
            if new_action.completed:
                if new_action.type == 'ban':
                    self.ban_actions.append(new_action)
                
                elif new_action.type == 'pick':
                    self.pick_actions.append(new_action)
            
    
    def sync_with_json(self, actions: list) -> None:
        pass
    
    def _iter_actions(self, actions: dict):
        for action_container in actions:
            for action in action_container:
                yield action
    

class TeamMember:
    '''Representation of user in session'''

    def __init__(self) -> None:
        self.assigned_position: str = None
        self.cell_id: int = None
        self.champion_id: int = None
        self.champion_pick_intent: int = None
        self.entitled_feature_type: str = None
        self.selected_skin_id: int = None
        self.spell1_id: int = None
        self.spell2_id: int = None
        self.summoner_id = None
        self.team: int = None
        self.ward_skin_id: int = None
    
    def _update_team_member(self, team_member: dict):
        '''This method assigns data to attributes based on provided json
        file. argument should be dictionary without any nested dictionaries.'''

        self.assigned_position: str = team_member['assignedPosition']
        self.cell_id: int = team_member['cellId']
        self.champion_id: int = team_member['championId']
        self.champion_pick_intent: int = team_member['championPickIntent']
        self.entitled_feature_type: str = team_member['entitledFeatureType']
        self.selected_skin_id: int = team_member['selectedSkinId']
        self.spell1_id: int = team_member['spell1Id']
        self.spell2_id: int = team_member['spell2Id']
        self.summoner_id = team_member['summonerId']
        self.team: int = team_member['team']
        self.ward_skin_id: int = team_member['wardSkinId']
        

class Team(ABC):
    '''Team interface, should be inherited by MyTeam and TheirTeam classes'''

    @abstractmethod
    def sync_with_websocket(self, team_members: list) -> None:
        '''Provided argument should privide list of team members (depending on
        team) and this method shoud initialize MyTeam object which contains
        all team members.'''
        pass

    @abstractmethod
    def sync_with_json(self, team_members: list) -> None:
        '''Provided argument should privide list of team members (depending on
        team) and this method shoud initialize MyTeam object which contains
        all team members.'''
        pass


class MyTeam(list, Team):
    def __init__(self, arg_session_manager: SessionManager) -> None:
        super().__init__()
        self.session_manager: SessionManager = arg_session_manager
        self.me: TeamMember = None
    
    def get_me(self) -> TeamMember:
        '''This method shouldn't iterate through MyTeam to find actions in
        progress. The variable should be updated by syn_with_websocket and
        always be updated.'''

        return self.me
    
    def sync_with_websocket(self, team_members: list) -> None:

        self.clear()
        # Iterate through all team members provied by argument (list from json)
        for _team_member in team_members:
            # Creagte new instance of member for each element from the list
            new_team_member: TeamMember = TeamMember()

            # Update attributes of this instance using helper method
            new_team_member._update_team_member(_team_member)
            # Apped new instance to object itself (MyTeam instance)
            self.append(new_team_member)

            # If newly created instance's summoner_id attribute is filled with
            # data wich value is equal to your user's summoner id update
            # self.me wich represents your character and and actions in
            # session (the myTeam part). Note that this is always checked
            # when sync occures (this is - when websocked is CREATED, UPDATED)
            if new_team_member.summoner_id == self.session_manager.SUMMONER_ID:
                self.me = new_team_member
    
    def sync_with_json(self, team_members: list) -> None:
        pass


class TheirTeam(list, Team):
    def __init__(self) -> None:
        super().__init__()