# class AFMbase(FabricationProcessStepBase):
#    m_def = Section(
#        a_eln={
#            'properties': {
#                'order': [
#                    'job_number',
#                    'name',
#                    'tag',
#                    'id_item_processed',
#                    'operator',
#                    'starting_date',
#                    'ending_date',
#                    'duration',
#                    'afm_tip',
#                    'afm_mode',
#                    'afm_setpoint',
#                    'afm_fb_gain',
#                    'afm_tip_resonance',
#                    'afm_tip_phase',
#                    'afm_laser_intensity',
#                    'afm_fb_gain_o',
#                    'notes',
#                ]
#            },
#        },
#    )
#
#    afm_tip = Quantity(
#        type=str,
#        description='the model of the probing tip',
#        a_eln={
#            'component': 'StringEditQuantity',
#        },
#    )
#
#    afm_mode = Quantity(
#        type=str,
#        description='if proxy or in contact, if linear or scanning',
#        a_eln={
#            'component': 'StringEditQuantity',
#        },
#    )
#
#    afm_setpoint = Quantity(
#        type=np.float64,
#        description='force applied to the tip',
#        a_eln={
#            'component': 'NumberEditQuantity',
#        },
#        unit='A',
#    )
#    afm_fb_gain = Quantity(
#        type=np.float64,
#        description='piezoelectric parameter',
#        a_eln={
#            'component': 'NumberEditQuantity',
#        },
#        unit='nm',
#    )
#    afm_tip_resonance = Quantity(
#        type=np.float64,
#        description='tip calibration parameter',
#        a_eln={
#            'component': 'NumberEditQuantity',
#        },
#        unit='MHz',
#    )
#    afm_tip_phase = Quantity(
#        type=np.float64,
#        description='tip calibration parameter',
#        a_eln={
#            'component': 'NumberEditQuantity',
#        },
#        unit='nm',
#    )
#    afm_laser_intensity = Quantity(
#        type=np.float64,
#        description='the laser source hitting the photodiode',
#        a_eln={
#            'component': 'NumberEditQuantity',
#        },
#        unit='mA',
#    )
#    afm_fb_gain_o = Quantity(
#        type=np.float64,
#        description='tip parameter',
#        a_eln={
#            'component': 'NumberEditQuantity',
#        },
#        unit='nm',
#    )
# m_package.__init_metainfo__()
